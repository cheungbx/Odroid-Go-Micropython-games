# invadero.py
#
# Use common game module "gameogo.py" for ESP32 Odroid Go
# by Billy Cheung  2019 10 26
#
#
import gc
import sys
gc.collect()
print (gc.mem_free())
import utime
from utime import sleep_ms
import network
from math import sqrt
# all dislplay, buttons, paddle, sound logics are in gameogo.py module
from gameogo import *
g=gameOGO()
g.tft.font(g.tft.FONT_Ubuntu)
COLOR_BG = g.tft.BLACK
COLOR_FG = g.tft.CYAN
COLOR_GUN = g.tft.GREEN
COLOR_Alien = g.tft.YELLOW
COLOR_SHIP1 = g.tft.BLUE
COLOR_SHIP2 = g.tft.RED
COLOR_BULLET = g.tft.BLUE
COLOR_ABULLET = g.tft.YELLOW
g.tft.set_bg(COLOR_BG)
g.tft.set_fg(COLOR_FG)
g.tft.font(g.tft.FONT_Ubuntu)
# songbuf = [ g.songStart, NotesorFreq , timeunit,
#             freq1, duration1, freq2, duration2,
#             g.songLoop  or g.songEnd]
# Notes or Freq : False=song coded frequencies (Hz), True=song coded in notes, e.g. 'f4' 'f#4')
# timeunit = value to multiple durations with that number of milli-seconds. Default 1 milli-second.
# freq1 can be replaced with note, e.g. [g.songStart, 'c4', 200,'d4', 200,'e4',300,'f4', 300,'f#4': 300,'g4',300,g.songEnd]
# freq1 = 0 for silence notes
# duration1 is multipled with tempo to arrive at a duration for the  note in millseconds

g.frameRate = 30
g.maxBgm = 3
bgmBuf= [
    [g.songStart, False, 1, g.songEnd],
    # Empire Strikes Back
    [ g.songStart,True, 100, 0, 4,
    'g4',2,'g4',2,'g4',2,'c5',8,'g5',8,0,4,'f5',2,'e5',2,'d5',2,'c6',8,'g5',8, 0,4, 'f5',2,'e5',2,'d5',2,'c6',8,'g5',8,0,4,'f5',2,'e5',2,'f5',2,'d5',8,0,8,
    'g4',2,'g4',2,'g4',2,'c5',8,'g5',8,0,4,'f5',2,'e5',2,'d5',2,'c6',8,'g5',8, 0,4, 'f5',2,'e5',2,'d5',2,'c6',8,'g5',8,0,4,'f5',2,'e5',2,'f5',2,'d5',8,0,8,
    'g4',4,'a4',4,0,4,'f5',2,'e5',2,'d5',2,'c5',1,0,1,'c5',2,'d5',1,'e5',1,'d5',2,'a4',2,'b4',4,
    'g4',4,'a4',4,0,4,'f5',2,'e5',2,'d5',2,'c5',1,0,1,'g5',2,0,1,'d5',1,'d5',4,0,4,
    'g4',4,'a4',4,0,4,'f5',2,'e5',2,'d5',2,'c5',1,0,1,'c5',2,'d5',1,'e5',1,'d5',2,'a4',2,'b4',4,
    'e5',1,0,1,'e5',2,'a5',2,'g5',2,'f5',2,'e5',2,'d5',2,'c5',2,'b4',2,'a4',2,'e5',8, 0, 8,
    g.songLoop],
    # The Imperial March
    [ g.songStart,False, 1, 0, 400,
    440, 400, 0, 100, 440, 400, 0, 100, 440, 400, 0,100, 349, 350, 523, 150,   440, 500, 349, 350, 523, 150, 440, 650, 0,500, 659, 500, 659, 500, 659, 500,  698, 350, 523, 150, 415, 500, 349, 350, 523, 150, 440, 650, 0, 500,
    880, 500, 440, 300, 440, 150, 880, 500, 830, 325, 784, 175, 740, 125, 698, 125,  740, 250, 0, 325,  445, 250, 622, 500, 587, 325,   554, 175,   523, 125,  466, 125,   523, 250,  0, 350,
    349, 250,  415, 500, 349, 350, 440, 125, 523, 500, 440, 375,   523, 125, 659, 650, 0, 500,349, 250,  415, 500, 349, 375, 523, 125, 440, 500,  349, 375,   523, 125, 440, 650,0, 650,
    880, 500, 440, 300, 440, 150, 880, 500, 830, 325, 784, 175, 740, 125, 698, 125,  740, 250, 0, 325,  445, 250, 622, 500, 587, 325,   554, 175,   523, 125,  466, 125,   523, 250,  0, 350,
    g.songLoop],
    # Tetris
    [ g.songStart,False,200, 0, 4,
    659,2, 494, 1, 523,1, 587,2, 523, 1, 493, 1, 440, 2, 440, 1, 523,1, 659,2,587,1,523,1,493,2, 493,1,523,1,587,2,659,2,523,2,440,2,440,2,0,2,587, 1,698,1,880,2,783,1,698,1,659,2,523,1,659,2,587,1,523,1,493,2,493,1,523,1,587,2,659,2,523,2,440,2,440,2,0,2,
    329,4,261,4,293,4,246,4,261,4,220,4,207,4,246,4,329,4,261,4,293,4,246,4,261,2,329,2,440,4,415,6,0,2,
    g.songLoop]
    ]
AlienRows = 5
AliensPerRow = 11
Spacing = 1.4
ColSize = int(g.screenW // ((AliensPerRow + 4) * Spacing))
AlienW = int(ColSize // Spacing)
RowSize = int(g.screenH // (AlienRows * 3))
AlienH = int(RowSize // Spacing)

screenL = ColSize
screenR = g.screenW - screenL
ShipBaseY = RowSize*1
AlienBaseX = ColSize * 2
AlienBaseY = RowSize * 2

AW2 = int(AlienW//2)
AH2 = int(AlienH//2)
AH3 = int(AlienH//3)
AW4 = int(AlienW//4)

GunW = int(AlienW * 1.5)
GunH = int (AlienH * 1.5)
GunBaseX = int((g.screenW - GunW ) // 2)
GunBaseY = g.screenH - GunH - 2

bulletW = 3
bulletH = int (GunH // 3)


vBullet =int (AlienH // 2)

vAlien = int (AlienW//2)

vGun = int(GunW // 3)

def setUpAliens ():
    y = AlienBaseY
    while y < AlienBaseY +  AlienRows * RowSize :
      x = AlienBaseX
      while x < AlienBaseX + AliensPerRow * ColSize:
        Aliens.append(Rect(x,y,AlienW, AlienH))
        x = x + ColSize
      y = y + RowSize

def drawSpaceships(posture) :
    COLOR = COLOR_SHIP1 if posture else COLOR_SHIP2
    for i in spaceships :
        g.tft.rect(i.x+AlienW, i.y, AlienW  , i.h , COLOR,COLOR)
        g.tft.rect(i.x, i.y+AH3+1, i.w, AH3, COLOR, COLOR)
        g.tft.rect(i.x+AlienW, i.y+AH3+1, AlienW, AH3, COLOR_BG, COLOR_BG)

def drawAliens (posture) :
  if posture :
    for i in Aliens :
        g.tft.rect(i.x, i.y, AlienW , AlienH, COLOR_Alien, COLOR_Alien)
        g.tft.rect(i.x+AW4, i.y+AH2+1, AW2, AH2,  COLOR_BG, COLOR_BG)
  else :
      for i in Aliens :
        g.tft.rect(i.x, i.y, AlienW , AlienH, COLOR_Alien, COLOR_Alien)
        g.tft.rect(i.x+AW4, i.y, AW2, AH2,  COLOR_BG, COLOR_BG)

def drawGun (x,y,w,h) :
  g.tft.rect(x+int(w//6*3), y, int(w//6), int(h//2),COLOR_GUN,COLOR_GUN)
  g.tft.rect(x, int(y+ h//2), w, int(h//2),COLOR_GUN,COLOR_GUN)

def drawBullets () :
  for b in bullets:
    # print("{} {} {} {}".format(b.x,b.y,b.w,b.h))
    g.tft.rect(b.x, b.y, b.w, b.h, COLOR_BULLET,COLOR_BULLET)

def drawAbullets () :
  for b in aBullets:
    g.tft.rect(b.x, b.y, b.w, b.h,COLOR_ABULLET,COLOR_ABULLET)

def drawScore () :
  g.tft.text( 0,0,'S:{}  '.format (score),COLOR_FG)
  g.tft.text(g.screenW//3,0,'L:{}  '.format (level),COLOR_FG)
  for i in range (0, life) :
      drawGun(int(g.screenW//3*2) + (GunW+2)*i, 0, GunW, GunH)
  for i in range (life, 3) :
      g.tft.rect(int(g.screenW//3*2) + (GunW+2)*i, 0, GunW, GunH, COLOR_BG, COLOR_BG)

exitGame = False
demoOn = False
while not exitGame:
  gameOver = False
  usePaddle = False
  if demoOn :
      demo = True
  else :
      demo = False
  life = 3
  updateMenu = True
  #menu screen

  g.startSong(bgmBuf[g.bgm])
  while True:
    if updateMenu :
        updateMenu = False

        g.tft.clear(COLOR_BG)
        g.tft.text(0,0,'Breakout', COLOR_FG)
        g.display_vol()
        g.tft.text(0,g.screenH * 1 // 8,    'A          Start',COLOR_FG)
        g.tft.text(0,g.screenH * 2 // 8,    'Menu   Quit',COLOR_FG)
        if usePaddle :
            g.tft.text(0,g.screenH // 8 * 3,'U          Paddle',COLOR_FG)
        else :
            g.tft.text(0,g.screenH // 8 * 3,'U          Button',COLOR_FG)
        if demo :
            g.tft.text(0,g.screenH // 8 * 4,'D          AI-Player', COLOR_FG)
        else :
            g.tft.text(0,g.screenH // 8 * 4,'D          1-Player',COLOR_FG)
        if g.bgm :
            g.tft.text(0,g.screenH // 8 * 7,'R          Background Music {}'.format(g.bgm), COLOR_FG)
        else :
            g.tft.text(0,g.screenH // 8 * 7,'R          Background Music Off', COLOR_FG)

        g.tft.text(0,g.screenH // 8 * 5,    'Sel + U/D Frame/s {}'.format(g.frameRate), COLOR_FG)
        g.tft.text(0,g.screenH // 8 * 6,    'Vol + U/D Loudness', COLOR_FG)

    sleep_ms(10)
    g.getBtn()
    if g.setVol() :
        updateMenu = True
    elif g.setFrameRate():
        updateMenu = True
    elif g.justReleased(g.btnMenu) :
        exitGame = True
        gameOver= True
        break
    elif g.justPressed(g.btnA) or demoOn :
        if demo :
            demoOn = True
            g.tft.clear(COLOR_BG)
            g.center_msg('Menu to Stop Demo', COLOR_FG, COLOR_BG)
            sleep_ms(1000)
        break
    elif g.justPressed(g.btnU) :
        usePaddle =  not usePaddle
        updateMenu = True
    elif g.justPressed(g.btnD) :
        demo = not demo
        updateMenu = True
    elif g.justPressed(g.btnR) :
        g.bgm = 0 if g.bgm >= g.maxBgm else g.bgm + 1
        if g.bgm :
            g.startSong(bgmBuf[g.bgm])
        else :
            g.stopSong()


        updateMenu = True
  #reset the game
  score = 0
  level = 0
  loadLevel = True
  frameCount = 0
  # Chance from 1 to 128
  aBulletChance = 0
  spaceshipChance = 1
  while not gameOver:
    lost = False
    frameCount = frameCount + 1 if frameCount < 100000 else 0

    if loadLevel :
      g.tft.clear(COLOR_BG)
      loadLevel = False
      AlienFrameRate  = 15
      AlienFrame = 0
      ShipFrameRate = 10
      ShipFrame = 0
      frameCount = 0
      postureA = False
      postureS = False
      spaceships = []
      Aliens = []
      bullets = []
      aBullets = []
      setUpAliens()
      Gun = Rect(GunBaseX, GunBaseY, GunW, GunH)
      aBulletChance = 5 + level * 5


    #generate space ships
    if g.random (0,200) < spaceshipChance and len(spaceships) < 1 :
      spaceships.append(Rect(AlienBaseX,ShipBaseY, AlienW*3, AlienH))

    if len(spaceships) :
      if abs(frameCount - ShipFrame) > ShipFrameRate  :
        ShipFrame = frameCount
        postureS = not postureS
        # move spaceships once every 4 frames
        for i in spaceships:
          g.tft.rect(i.x, i.y, i.w, i.h, COLOR_BG, COLOR_BG)
          i.move(g.screenW // 16,0)
          if i.x >= screenR :
            spaceships.remove(i)
      if frameCount % 20 == 10 :
        g.playTone ('e5', 20)
      elif frameCount % 20 == 0 :
        g.playTone ('c5', 20)


    if abs(frameCount - AlienFrame) > AlienFrameRate  :
      AlienFrame = frameCount
      postureA = not postureA
      # move Aliens once every 15 frames
      # if postureA :
      #    g.playSound (80, 10)
      # else:
      #    g.playSound (120, 10)

      for i in Aliens :
          g.tft.rect(i.x,i.y,i.w,i.h, COLOR_BG, COLOR_BG) # Erase Aliens
      for i in Aliens:
        if i.x > screenR or i.x < screenL :
            vAlien = -vAlien
            for Alien in Aliens :
              Alien.move (0, RowSize)
              if Alien.y + Alien.h > Gun.y :
                lost = True
                loadLevel = True
                g.playTone ('f4',300)
                g.playTone ('d4',100)
                g.playTone ('c5',100)
                break
            break

      for i in Aliens :
        i.move (vAlien, 0)


    g.getBtn()
    newX = Gun.x
    fired = False
    if g.justPressed (g.btnMenu) :
        gameOver = True
        demoOn = False

    if demo :  # AI Player
        if g.random (0,1) and len(bullets) < 2:
            fired = True

        newX = Gun.x + vGun if g.random(0,1) else Gun.x - vGun


    else:    # Real player
        if g.justPressed (g.btnA | g.btnB) and len(bullets) < 2:
            fired = True
        elif g.pressed (g.btnL) :
            newX = Gun.x-vGun
        elif g.pressed(g.btnR) :
            newX = Gun.x+vGun
        if usePaddle :
            newX = int(g.getPaddle() / (1024/(screenR-screenL)))

    if fired :
        bullets.append(Rect(int(Gun.x+GunW//2),int(Gun.y), bulletW, bulletH))
        g.playSound (200,5)
        g.playSound (300,5)
        g.playSound (400,5)

    if newX != Gun.x and 0 < newX < g.screenW :
        g.tft.rect(Gun.x,Gun.y,Gun.w,Gun.h, COLOR_BG, COLOR_BG) # erase gun
        Gun.x = newX


    # move bullets

    for b in bullets:
      # erase bullets
      # print("{} {} {} {}".format(b.x,b.y,b.w,b.h))
      g.tft.rect(b.x, b.y, b.w, b.h, COLOR_BG, COLOR_BG)
      b.move(0,-vBullet)
      if b.y < 0 :
        bullets.remove(b)
      else :
        for i in Aliens:
          if i.colliderect(b) :
            # erase Aliens
            g.tft.rect(i.x, i.y, i.w, i.h, COLOR_BG, COLOR_BG)
            Aliens.remove(i)
            bullets.remove(b)
            score +=1
            g.playTone ('c6',10)
            # adjist Alien move rate
            AlienFrameRate = (2 + int (len(Aliens) / 55 * 13 ))
            break
        for i in spaceships :
          if i.colliderect(b) :
            # erase Spaceship
            g.tft.rect(i.x, i.y, i.w, i.h, COLOR_BG, COLOR_BG)
            spaceships.remove(i)
            bullets.remove(b)
            score +=10
            g.playTone ('b4',30)
            g.playTone ('e5',10)
            g.playTone ('c4',30)
            break

    # Launch Alien bullets
    for i in Aliens:
        if g.random (0,1000) * len (Aliens) * 10 < aBulletChance and len(aBullets) < 3 :
            aBullets.append(Rect(int(i.x+AlienW//2), i.y,  bulletW, bulletH))
    # move Alien bullets
    for b in aBullets:
        g.tft.rect(b.x, b.y, b.w, b.h, COLOR_BG, COLOR_BG)
        b.move(0,vBullet)
        if b.y > g.screenH  :
            aBullets.remove(b)
        elif b.colliderect(Gun) :
            lost = True
            #print ('{} {} {} {} : {} {} {} {}'.format(b.x,b.y,b.x2,b.y2,Gun.x,Gun.y,Gun.x2,Gun.y2))
            aBullets.remove(b)
            g.playTone ('c5',30)
            g.playTone ('e4',30)
            g.playTone ('b4',30)
            break

    drawSpaceships (postureS)
    drawAliens (postureA)
    drawGun(Gun.x,Gun.y,Gun.w,Gun.h)
    drawBullets()
    drawAbullets()
    drawScore()


    if len(Aliens) == 0 :
      level += 1
      loadLevel = True
      g.playTone ('c4',100)
      g.playTone ('d4',100)
      g.playTone ('e4',100)
      g.playTone ('f4',100)
      g.playTone ('g4',100)
      g.bgm = 0 if g.bgm >= g.maxBgm else g.bgm + 1
      if g.bgm :
        g.startSong(bgmBuf[g.bgm])

    if lost :
      lost = False;
      life -= 1
      g.playTone ('f4',100)
      g.playTone ('g4',100)
      g.playTone ('c4',100)
      g.playTone ('d4',100)
      sleep_ms (1000)
      if life < 0 :
        gameOver = True

    if gameOver :

      g.center_msg ("GAME OVER",COLOR_FG,COLOR_BG)
      g.playTone ('b4',300)
      g.playTone ('e4',100)
      g.playTone ('c4',100)
      sleep_ms(2000)

    g.wait()

g.deinit()
del sys.modules["gameogo"]
gc.collect()
