# pongs.py
#
# Use common game module "gameogo.py" for ESP32 Odroid Go
# by Billy Cheung  2019 10 26
#
import gc
import sys
gc.collect()
print (gc.mem_free())
import utime
import network
from utime import sleep_ms
from utime import sleep_ms
# all dislplay, buttons, paddle, sound logics are in gameogo.py module
from gameogo import *
g=gameOGO()

fontW, fontH = g.tft.fontSize()


COLOR_MENU    = g.tft.YELLOW
COLOR_FG      = g.tft.GREEN
COLOR_BG      = g.tft.BLACK
COLOR_BRICK   = g.tft.RED
COLOR_BAT     = g.tft.GREEN
COLOR_BALL    = g.tft.BLUE
COLOR_SCORE   = g.tft.WHITE

scores = [0,0]
maxScore = 15
gameOver = False
exitGame = False


class bat(Rect):
  def __init__(self, velocity, up_key, down_key, *args, **kwargs):
    self.velocity = velocity
    self.up_key = up_key
    self.down_key = down_key
    super().__init__(*args, **kwargs)

  def move_bat(self, board_height, bat_HEIGHT, ballY):
    g.getBtn()

    if self.up_key == 0  : # use AI
      self.y = max(min(ballY - int(bat_HEIGHT /2) +  g.random(0,int(bat_HEIGHT *0.8)), board_height-bat_HEIGHT),0)

    elif self.up_key == -1 : # use Paddle
      self.y = int (g.getPaddle() / (1024 / (board_height-pong.bat_HEIGHT)))

    else :
      if g.pressed(self.up_key):
          self.y = max(self.y - self.velocity,0)
      if g.pressed(self.down_key):
          self.y = min(self.y + self.velocity, board_height-pong.bat_HEIGHT)

class Ball(Rect):
    def __init__(self, velocity, *args, **kwargs):
        self.velocity = velocity
        self.angle = 0
        super().__init__(*args, **kwargs)

    def move_ball(self):
        self.x += self.velocity
        self.y += self.angle


class Pong:
    HEIGHT = 240
    WIDTH = 320
    ScreenL = 10
    ScreenR = 310

    bat_WIDTH = 5
    bat_HEIGHT = 40
    bat_VELOCITY = 5
    BALL_WIDTH = 8
    BALL_R = int (BALL_WIDTH // 2)
    BALL_VELOCITY = 5
    BALL_ANGLE = 0
    scores = [0,0]
    maxScore = 15


    def init (self, onePlayer, demo, usePaddle):
        # Setup the screen
        global scores
        scores = [0,0]
        # Create the player objects.
        self.bats = []
        self.balls = []

        if demo :
          self.bats.append(bat(  # The left bat, AI
            self.bat_VELOCITY,
            0,
            0,
            self.ScreenL,
            int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
            self.bat_WIDTH,
            self.bat_HEIGHT))
        elif usePaddle :
          self.bats.append(bat(  # The left bat, use Paddle
            self.bat_VELOCITY,
            -1,
            -1,
            self.ScreenL,
            int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
            self.bat_WIDTH,
            self.bat_HEIGHT))
        else :

          self.bats.append(bat(  # The left bat, button controlled
            self.bat_VELOCITY,
            g.btnU,
            g.btnD,
            self.ScreenL,
            int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
            self.bat_WIDTH,
            self.bat_HEIGHT))

        if demo or onePlayer:
          self.bats.append(bat(  # The right bat, AI
              self.bat_VELOCITY,
              0,
              0,
              self.ScreenR,
              int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
              self.bat_WIDTH,
              self.bat_HEIGHT
              ))
        else :
           self.bats.append(bat(  # The right bat, button controlled
              self.bat_VELOCITY,
              g.btnB,
              g.btnA,
              self.ScreenR,
              int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
              self.bat_WIDTH,
              self.bat_HEIGHT
              ))

        self.balls.append(Ball(
            self.BALL_VELOCITY,
            int(self.WIDTH / 2 - self.BALL_WIDTH / 2),
            int(self.HEIGHT / 2 - self.BALL_WIDTH / 2),
            self.BALL_WIDTH,
            self.BALL_WIDTH))


    def score(self, player, ball):
      global gameOver
      global scores
      scores[player] += 1
      g.tft.circle(ball.x+self.BALL_R,ball.y+self.BALL_R,self.BALL_R, COLOR_BG, COLOR_BG)
      ball.velocity = - ball.velocity
      ball.angle = g.random(0,3) - 2
      ball.x = int(self.WIDTH / 2 - self.BALL_WIDTH / 2)
      ball.y = int(self.HEIGHT / 2 - self.BALL_WIDTH / 2)
      g.playTone ('g4', 100)

      if scores[player] >= maxScore :
        gameOver = True

    def check_ball_hits_wall(self):
      for ball in self.balls:

        if ball.x < self.ScreenL:
          self.score(1, ball)


        if ball.x > self.ScreenR :
          self.score(0, ball)


        if ball.y > self.HEIGHT - self.BALL_WIDTH or ball.y < 0:
          ball.angle = -ball.angle


    def check_ball_hits_bat(self):
      for ball in self.balls:
          for bat in self.bats:
            if ball.colliderect(bat):
                  ball.velocity = -ball.velocity
                  ball.angle = g.random (0,3) - 2
                  g.playTone ('c6', 10)
                  break

    def game_loop(self):
      global gameOver, exitGame, scores
      demoOn = False
      demo = False
      exitGame = False
      onePlayer = True
      usePaddle = False


      while not exitGame:
        if demoOn :
            playsers = 0
            demo = True
        else :
            players = 1
            demo = False

        gameOver = False

        updateMenu = True

        while True:
            if updateMenu :
                updateMenu = False
                g.tft.clear(COLOR_BG)
                g.tft.text(0,0,'Pong ', COLOR_FG)
                g.display_vol()
                g.tft.text(0,g.screenH * 1 // 7,    'A          Start',COLOR_FG)
                g.tft.text(0,g.screenH * 2 // 7,    'Menu   Quit',COLOR_FG)
                if usePaddle :
                    g.tft.text(0,g.screenH // 7 * 3,'U          Paddle',COLOR_FG)
                else :
                    g.tft.text(0,g.screenH // 7 * 3,'U          Button',COLOR_FG)
                if players == 0 :
                    g.tft.text(0,g.screenH // 7 * 4,'D          AI-Player', COLOR_FG)
                elif players == 1 :
                    g.tft.text(0,g.screenH // 7 * 4,'D          1-Player',COLOR_FG)
                else :
                    g.tft.text(0,g.screenH // 7 * 4,'D          2-Player',COLOR_FG)
                g.tft.text(0,g.screenH // 7 * 5,     'Sel + U/D Frame/s {}'.format(g.frameRate), COLOR_FG)
                g.tft.text(0,g.screenH // 7 * 6,     'Vol + U/D Loudness', COLOR_FG)


            sleep_ms(10)
            g.getBtn()
            if g.setVol() :
                updateMenu = True
            elif g.setFrameRate() :
                updateMenu = True
            elif g.justReleased(g.btnMenu) :
                exitGame = True
                gameOver= True
                break
            elif g.justPressed(g.btnA) or demoOn :
                if players == 0 : # demo
                    onePlayer = False
                    demo = True
                    demoOn = True
                    g.tft.clear(COLOR_BG)
                    g.center_msg('Demo Menu to Stop', COLOR_FG, COLOR_BG)
                    sleep_ms(1000)

                elif players == 1 :
                    onePlayer = True
                    demo = False
                else :
                    onePlayer = False
                    demo = False
                break
            elif g.justPressed(g.btnU) :
                usePaddle =  not usePaddle
                updateMenu = True
            elif g.justPressed(g.btnD) :
                players = (players + 1) % 3
                updateMenu = True

        self.init(onePlayer, demo, usePaddle)

        g.tft.clear(COLOR_BG)

        for bat in self.bats:
            g.tft.rect(bat.x,bat.y,self.bat_WIDTH, self.bat_HEIGHT, COLOR_BAT, COLOR_BAT)

        while not gameOver:
          g.getBtn()
          if g.justReleased(g.btnMenu) :
            gameOver = True
            demoOn = False


          self.check_ball_hits_bat()
          self.check_ball_hits_wall()

          for bat in self.bats:
            prev_y = bat.y
            bat.move_bat(self.HEIGHT, self.bat_HEIGHT, self.balls[0].y)
            if prev_y != bat.y :
                g.tft.rect(bat.x,prev_y,self.bat_WIDTH, self.bat_HEIGHT, COLOR_BG, COLOR_BG)
                g.tft.rect(bat.x,bat.y,self.bat_WIDTH, self.bat_HEIGHT, COLOR_BAT, COLOR_BAT)

          for ball in self.balls:
            g.tft.circle(ball.x+self.BALL_R,ball.y+self.BALL_R,self.BALL_R, COLOR_BG, COLOR_BG)
            ball.move_ball()
            g.tft.circle(ball.x+self.BALL_R,ball.y+self.BALL_R,self.BALL_R, COLOR_BALL, COLOR_BALL)


          g.tft.text ( 120, 0,'{}    :    {}  '.format (scores[0], scores[1]), COLOR_FG)

          if gameOver :
            g.center_msg ("Game Over", COLOR_FG, COLOR_BG)
            g.playTone ('c5', 200)
            g.playTone ('g4', 200)
            g.playTone ('g4', 200)
            g.playTone ('a4', 200)
            g.playTone ('g4', 400)
            g.playTone ('b4', 200)
            g.playTone ('c5', 400)

          g.wait()


#if __name__ == '__main__':
pong = Pong()

pong.game_loop()


g.deinit()
del sys.modules["gameogo"]
gc.collect()

print ("game exit")
