# gameESP.py
# for ESP32 Odroid-go
# common micropython module for ESP32 game board designed by Billy Cheung (c) 2019 08 31
# --usage--
# Using this common micropython game module, you can write micropython games to run
# either on the SPI OLED or I2C OLED without chaning a line of code.
# You only need to set the following line in gameESP.py file at the __init__ function
#        self.useSPI = True  # for SPI display , with buttons read through ADC
#        self.useSPI = False  # for I2C display, and individual hard buttons
#
# Note:  esp32 without the PSRAM only have 100K of RAM and is very bad at running .py micropython source code files
# with its very limited CPU onboard memory of 100K
# so to run any program with > 300 lines of micropython codes combined (including all modules),
# you need to convert source files into byte code first to avoid running out of memory.
# Install a version of the  mpy-cross micropython pre-compiler that can run in your system (available from github).
# Type this command to convert gameESP.py to the byte code file gameESP.mpy  using mpy-cross.
#        mpy-cross gameESP.py
# then copy the gameESP.mpy file to the micropython's import directory on the flash
# create your game and leaverge the functions to display, read buttons and paddle and make sounds
# from the gameESP class module.
# Add this line to your micropython game source code (examples attached, e.self. invader.py)
#       from gameESP import gameESP, Rect
#       g=GameESP()
#
#
#
#-----------------------------------------
'''
ESP32 Game board
TFT ILI9341 SPI
================
VCC     -  3V3
GND     -  GND
D0/SCK  -  IO18-VSPI-SCK
D1/MOSI -  IO23-VSPI-MOSI
RES     -  IO4 for ESP32
DC      -  IO21
CS      -  IO5-VSPI CS0
LED/BLK -  IO14
MISO    -  IO19-VSPI-MISO (not required for OLED)
TF Card Odroid-go
================
CS     -   IO22 VSPI CS1
MOSI   -   IO23 VSPI MOSI
MISO   -   IO19 VSPI SCK
SCK    -   IO18 VSPI MISO
Power
======
GND-100K-IO36(VP)-100K-VBat(3.7V)
GND-0.1uF-IO36
Audio
======
Speaker- - GND
Speaker+ - 10K VR- IO26
Paddle
======
GND
VN/IO39
4.7K-VCC
D-PAD Buttons
=============
tie one end to 3V3
UP        IO35-10K-GND
Down-10K  IO35
Left      IO34-10K-GND
Right-10K IO34
Other Buttons
============
tie one end to GND
Menu      IO13
Volume    IO00-10K-3v3
Select    IO27
Start     IO39(VN)-10K-3v3
B         IO33
A         IO32
'''
import utime
from utime import sleep_ms,ticks_ms, ticks_us, ticks_diff
from machine import Pin, SPI, PWM, ADC
from random import randint, seed
from micropython import const
import display

TFT_DC_PIN = const(21)
TFT_CS_PIN = const(5)
TFT_LED_PIN = const(14)
TFT_MOSI_PIN = const(23)
TFT_MISO_PIN = const(19)
TFT_SCLK_PIN = const(18)

BUTTON_A_PIN = const(33)
BUTTON_B_PIN = const(32)
BUTTON_MENU_PIN = const(13)
BUTTON_SELECT_PIN = const(27)
BUTTON_VOLUME_PIN = const(0)
BUTTON_START_PIN = const(39)
BUTTON_JOY_Y_PIN = const(35)
BUTTON_JOY_X_PIN = const(34)
BUTTON_DEBOUNCE_MS = const(5)

SPEAKER_PIN = const(26)
SPEAKER_DAC_PIN = const(25)
SPEAKER_TONE_CHANNEL = const(0)

#PADDLE_PIN = const(39)
BATTERY_PIN = const(36)
BATTERY_RESISTANCE_NUM = const(2)



class gameOGO():
    max_vol = 6
    duty={0:0,1:0.05,2:0.1,3:0.5,4:1,5:2,6:70}
    tones = {
        'c4': 262,
        'd4': 294,
        'e4': 330,
        'f4': 349,
        'f#4': 370,
        'g4': 392,
        'g#4': 415,
        'a4': 440,
        "a#4": 466,
        'b4': 494,
        'c5': 523,
        'c#5': 554,
        'd5': 587,
        'd#5': 622,
        'e5': 659,
        'f5': 698,
        'f#5': 740,
        'g5': 784,
        'g#5': 831,
        'a5': 880,
        'b5': 988,
        'c6': 1047,
        'c#6': 1109,
        'd6': 1175,
        ' ': 0
    }

    def __init__(self):
        # True =  SPI display, False = I2C display
        self.ESP32 = True
        self.useSPI = True
        self.timer = 0
        self.vol = int(self.max_vol/2) + 1
        seed(ticks_us())
        self.btnU = 1 << 1
        self.btnL = 1 << 2
        self.btnR = 1 << 3
        self.btnD = 1 << 4
        self.btnA = 1 << 5
        self.btnB = 1 << 6
        self.btnMenu = 1 << 7
        self.btnVol  = 1 << 8
        self.btnSel  = 1 << 9
        self.btnSt   = 1 << 10

        self.btnUval = 0
        self.btnDval = 0
        self.btnLval = 0
        self.btnRval = 0
        self.btnAval = 0
        self.btnBval = 0
        self.btnMenuval = 0
        self.btnVolval  = 0
        self.btnSelval  = 0
        self.btnStval   = 0
        self.frameRate  = 30

        self.Btns = 0
        self.lastBtns = 0

        self.PinBuzzer = Pin(26, Pin.OUT)

        self.tft = display.TFT()
        self.tft.init(self.tft.ILI9341, width=240, height=320, speed=40000000, backl_pin=14, backl_on=1, miso=19, mosi=23, clk=18, cs=5, dc=21, hastouch=False)
        self.tft.clear(self.tft.BLACK)
        self.tft.orient(self.tft.LANDSCAPE_FLIP)
        self.screenW, self.screenH = self.tft.screensize()
        ''' fonts available in ili9341
        tft.FONT_Small, 8x12
        tft.FONT_Default, 13x13
        tft.FONT_7seg, 18x31
        tft.FONT_Ubuntu, 15x16
        tft.FONT_Comic, 25x28
        tft.FONT_Tooney, 32x37
        tft.FONT_Minya, 20x24
        '''
        self.tft.font(self.tft.FONT_Ubuntu, rotate=0)

        self.PinBtnA  = Pin(BUTTON_A_PIN, Pin.IN, Pin.PULL_UP)
        self.PinBtnB  = Pin(BUTTON_B_PIN, Pin.IN, Pin.PULL_UP)
        self.PinBtnMenu  = Pin(BUTTON_MENU_PIN, Pin.IN, Pin.PULL_UP)
        self.PinBtnVol  = Pin(BUTTON_VOLUME_PIN, Pin.IN, Pin.PULL_UP)
        self.PinBtnSel  = Pin(BUTTON_SELECT_PIN, Pin.IN, Pin.PULL_UP)
        self.PinBtnSt   = Pin(BUTTON_START_PIN, Pin.IN)


        self.adcX = ADC(BUTTON_JOY_X_PIN)
        self.adcY = ADC(BUTTON_JOY_Y_PIN)
        #self.adc = ADC(PADDLE_PIN)
        self.adcX.atten(ADC.ATTN_11DB)
        self.adcY.atten(ADC.ATTN_11DB)
        #self.adc.atten(ADC.ATTN_11DB)


    def deinit(self) :
      #self.adc.deinit()
      self.adcX.deinit()
      self.adcY.deinit()
      self.tft.deinit()


    def getPaddle (self) :
      return 512
      # ESP32 - 142 to 3155
      # return max ( min (int (self.adc.read() / 2.935) - 48, 1023),0)

    def pressed (self,btn) :
      return (self.Btns & btn)

    def justPressed (self,btn) :
      return (self.Btns & btn) and not (self.lastBtns & btn)

    def justReleased (self,btn) :
      return (self.lastBtns & btn) and not (self.Btns & btn)

    def getBtn(self) :

        self.btnAval = not self.PinBtnA.value()
        self.btnBval = not self.PinBtnB.value()
        self.btnMenuval =  not self.PinBtnMenu.value()
        self.btnVolval  =  not self.PinBtnVol.value()
        self.btnSelval  =  not self.PinBtnSel.value()
        self.btnStval   =  not self.PinBtnSt.value()

        val = self.adcX.read()
        self.btnLval = 1 if val > 2500  else 0
        self.btnRval = 1 if 1500 < val < 2000 else 0

        val = self.adcY.read()
        self.btnUval = 1 if val > 2500  else 0
        self.btnDval = 1 if 1500 < val < 2000 else 0

        self.lastBtns = self.Btns
        self.Btns = 0
        self.Btns = self.Btns | self.btnUval << 1 | self.btnLval << 2 | self.btnRval << 3 | self.btnDval << 4 | self.btnAval << 5 | self.btnBval << 6
        self.Btns = self.Btns | self.btnMenuval << 7 | self.btnVolval << 8 | self.btnSelval << 9 | self.btnStval << 10

        return self.Btns

    def setVol(self) :
        if self.pressed(self.btnVol):
            if self.justPressed(self.btnU) :
                self.vol= min (self.vol+1, self.max_vol)
                self.playTone('c4', 100)
                return True
            elif self.justPressed(self.btnD) :
                self.vol= max (self.vol-1, 0)
                self.playTone('d4', 100)
                return True
        return False

    def setFrameRate(self) :
        if self.pressed(self.btnSel):
            if self.justPressed(self.btnU) :
                self.frameRate = self.frameRate + 5 if self.frameRate < 100 else 5
                self.playTone('e4', 100)
                return True
            elif self.justPressed(self.btnD) :
                self.frameRate = self.frameRate - 5 if self.frameRate > 5 else 100
                self.playTone('f4', 100)
                return True
        return False

    def center_msg (self, msg, color_fg, color_bg) :
        self.tft.set_bg(color_bg)
        self.tft.textClear((self.screenW - self.tft.textWidth(msg)) //2, self.screenH//2, msg, color_bg)
        self.tft.text((self.screenW - self.tft.textWidth(msg)) //2, self.screenH//2, msg, color_fg)


    def display_msg (self, x, y, msg, color_fg, color_bg) :
        self.tft.set_bg(color_bg)
        self.tft.textClear(x, y , msg, color_bg)
        self.tft.text(x, y, msg, color_fg)



    def display_vol(self) :
        fontW, fontH = self.tft.fontSize()
        self.tft.rect(self.screenW-fontW*self.max_vol,0, self.max_vol*fontW,fontH, self.tft.GREEN,self.tft.BLACK)
        self.tft.rect(self.screenW-fontW*self.max_vol+1, 1, self.vol * fontW-2,fontH-2, self.tft.RED, self.tft.RED)

    def playTone(self, tone, tone_duration, rest_duration=0):
        beeper = PWM(self.PinBuzzer, freq=self.tones[tone], duty=self.duty[self.vol])
        sleep_ms(tone_duration)
        beeper.deinit()
        sleep_ms(rest_duration)

    def playSound(self, freq, tone_duration, rest_duration=0):
        beeper = PWM(self.PinBuzzer, freq, duty=self.duty[self.vol])
        sleep_ms(tone_duration)
        beeper.deinit()
        sleep_ms(rest_duration)

    def random (self, x, y) :
        return  randint(x,y)

    def wait(self) :
        timer_dif = int(1000/self.frameRate) - ticks_diff(ticks_ms(), self.timer)
        if timer_dif > 0 :
            sleep_ms(timer_dif)
        self.timer=ticks_ms()


class Rect (object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


    def move (self, vx, vy) :
        self.x = self.x + vx
        self.y = self.y + vy


    def colliderect (self, rect1) :
      if (self.x + self.w   > rect1.x and
        self.x < rect1.x + rect1.w  and
        self.y + self.h > rect1.y and
        self.y < rect1.y + rect1.h) :
        return True
      else:
        return False
