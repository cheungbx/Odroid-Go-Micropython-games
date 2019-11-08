# btntests.py
# button , paddle, speaker and display tester for game board
# Use common game module "gameogo.py" for ESP32 Odroid Go
# by Billy Cheung  2019 10 26
#
#  ESP32 Game board (follow same pin layout as the Odroid_go)

# OLED SPI
# ========
# VCC    -        3V3
# GND    -       GND
# D0/SCK  -   IO18-VSPI-SCK
# D1/MOSI  - IO23-VSPI-MOSI
# RES        -    IO4 for ESP32
# DC         -      IO21
# CS          -      IO5-VSPI CS0
# LED/BLK -    IO14

# MISO     -      IO19-VSPI-MISO

# Audio
# ======
# Speaker-  GND
# Speaker+ - 10K VR- IO26

# Paddle (10K VR)
# ======
# GND
# VN/IO39
# -VCC
#
# D-PAD Buttons
# =============
# tie one end to 3V3
# UP              IO35-10K-GND
# Down-10K IO35
# Left            IO34-10K-GND
# Right-10K IO34

# Other Buttons
# ============
# tie one end to GND
# Menu    IO13
# Volume IO00-10K-3v3
# Select   IO27
# Start     IO39(VN)-10K-3v3
# B           IO33
# A           IO32
#

import gc
import sys
gc.collect()
print (gc.mem_free())
import network
import utime
from utime import sleep_ms,ticks_ms, ticks_us, ticks_diff
from machine import  ADC
# all dislplay, buttons, paddle, sound logics are in game32.mpy module
from gameogo import *
g=gameOGO()
tone_dur = 20
COLOR_BG = g.tft.BLACK
COLOR_FG = g.tft.GREEN

fontW, fontH = g.tft.fontSize()
g.tft.clear(COLOR_BG)
g.tft.text( g.screenW//3*2,0,"L+A=Exit")

while True :

    g.getBtn()
    g.setVol()

    COLOR_FG = g.tft.GREEN
    COLOR_BG = g.tft.BLACK
    g.tft.set_bg(COLOR_BG)
    g.tft.text (0,0,"P:{}   ".format(g.getPaddle()), COLOR_FG)
    g.tft.text (g.screenW//3,0,"V:{}   ".format(g.vol),COLOR_FG)

    g.tft.text (0,fontH+2,"X:{}   ".format(g.adcX.read()), COLOR_FG)

    g.tft.text (g.screenW//3,fontH+2,"Y:{}   ".format(g.adcY.read()), COLOR_FG)


    if g.pressed(g.btnL) and g.pressed(g.btnA):
        g.center_msg ("Bye!", COLOR_FG, COLOR_BG)
        g.playTone('e4', tone_dur)
        g.playTone('c4', tone_dur)
        break


    if g.pressed (g.btnMenu):
        COLOR_FG = g.tft.BLACK
        COLOR_BG = g.tft.GREEN
        g.playTone('b4', tone_dur)
    else :
        COLOR_FG = g.tft.GREEN
        COLOR_BG = g.tft.BLACK
    g.display_msg(0, g.screenH//6 * 2 , "Menu", COLOR_FG,COLOR_BG)

    if g.pressed (g.btnVol):
        COLOR_FG = g.tft.BLACK
        COLOR_BG = g.tft.GREEN
        g.playTone('c5', tone_dur)
    else :
        COLOR_FG = g.tft.GREEN
        COLOR_BG = g.tft.BLACK
    g.display_msg(g.screenW//4, g.screenH//6 * 2 , "Volume", COLOR_FG,COLOR_BG)

    if g.pressed (g.btnSel):
        COLOR_FG = g.tft.BLACK
        COLOR_BG = g.tft.GREEN
        g.playTone('d5', tone_dur)
    else :
        COLOR_FG = g.tft.GREEN
        COLOR_BG = g.tft.BLACK
    g.display_msg(g.screenW//4 * 2, g.screenH//6 * 2 , "Select", COLOR_FG,COLOR_BG)

    if g.pressed (g.btnSt):
        COLOR_FG = g.tft.BLACK
        COLOR_BG = g.tft.GREEN
        g.playTone('e5', tone_dur)
    else :
        COLOR_FG = g.tft.GREEN
        COLOR_BG = g.tft.BLACK
    g.display_msg(g.screenW//4 * 3, g.screenH//6 * 2, "Start", COLOR_FG,COLOR_BG)

    if g.pressed(g.btnU):
        COLOR_FG = g.tft.BLACK
        COLOR_BG = g.tft.GREEN
        g.playTone('c4', tone_dur)
    else :
        COLOR_FG = g.tft.GREEN
        COLOR_BG = g.tft.BLACK

    g.display_msg(g.screenW//6, g.screenH//6 * 3, "U", COLOR_FG,COLOR_BG)


    if g.pressed(g.btnL):
      COLOR_FG = g.tft.BLACK
      COLOR_BG = g.tft.GREEN
      g.playTone('d4', tone_dur)
    else :
      COLOR_FG = g.tft.GREEN
      COLOR_BG = g.tft.BLACK
    g.display_msg( 0, g.screenH//6 * 4, "L", COLOR_FG,COLOR_BG)


    if g.pressed(g.btnR):
      COLOR_FG = g.tft.BLACK
      COLOR_BG = g.tft.GREEN
      g.playTone('e4', tone_dur)
    else :
       COLOR_FG = g.tft.GREEN
       COLOR_BG = g.tft.BLACK
    g.display_msg( g.screenW//6 * 2, g.screenH//6 * 4,"R", COLOR_FG,COLOR_BG)

    if g.pressed (g.btnD):
      COLOR_FG = g.tft.BLACK
      COLOR_BG = g.tft.GREEN
      g.playTone('f4', tone_dur)
    else :
       COLOR_FG = g.tft.GREEN
       COLOR_BG = g.tft.BLACK

    g.display_msg(g.screenW//6  , g.screenH//6 * 5,"D", COLOR_FG,COLOR_BG)


    if g.pressed(g.btnA):
      COLOR_FG = g.tft.BLACK
      COLOR_BG = g.tft.GREEN
      g.playTone('g4', tone_dur)
    else :
       COLOR_FG = g.tft.GREEN
       COLOR_BG = g.tft.BLACK
    g.display_msg(g.screenW//6 * 4 , g.screenH//6 * 5, "A", COLOR_FG,COLOR_BG)


    if g.pressed(g.btnB):
      COLOR_FG = g.tft.BLACK
      COLOR_BG = g.tft.GREEN
      g.playTone('a4', tone_dur)
    else :
       COLOR_FG = g.tft.GREEN
       COLOR_BG = g.tft.BLACK
    g.display_msg(g.screenW//6 * 5 , g.screenH//6 * 4, "B", COLOR_FG,COLOR_BG)


    sleep_ms(5)


g.deinit()
del sys.modules["gameogo"]
gc.collect()
