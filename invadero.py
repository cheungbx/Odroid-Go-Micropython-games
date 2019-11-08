# Aliens.py
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

g.frameRate = 30


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
  while True:
    if updateMenu :
        updateMenu = False

        g.tft.clear(COLOR_BG)
        g.tft.text(0,0,'Breakout', COLOR_FG)
        g.display_vol()
        g.tft.text(0,g.screenH * 1 // 7,    'A          Start',COLOR_FG)
        g.tft.text(0,g.screenH * 2 // 7,    'Menu   Quit',COLOR_FG)
        if usePaddle :
            g.tft.text(0,g.screenH // 7 * 3,'U          Paddle',COLOR_FG)
        else :
            g.tft.text(0,g.screenH // 7 * 3,'U          Button',COLOR_FG)
        if demo :
            g.tft.text(0,g.screenH // 7 * 4,'D          AI-Player', COLOR_FG)
        else :
            g.tft.text(0,g.screenH // 7 * 4,'D          1-Player',COLOR_FG)
        g.tft.text(0,g.screenH // 7 * 5,     'Sel + U/D Frame/s {}'.format(g.frameRate), COLOR_FG)
        g.tft.text(0,g.screenH // 7 * 6,     'Vol + U/D Loudness', COLOR_FG)

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
      if postureA :
          g.playSound (80, 10)
      else:
          g.playSound (120, 10)

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
