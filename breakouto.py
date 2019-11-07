# ----------------------------------------------------------
#  Breakout.py  Game
# Use common game module "gameESP.py" for ESP8266  or ESP32
# by Billy Cheung  2019 10 26
#
import sys
import gc
gc.collect()
# # print (gc.mem_free())
import math
from math import sqrt
import network
import utime
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




class Ball(object):
    """Ball."""

    def __init__(self, x, y, x_speed, y_speed, tft, width=8, height=8,
                 frozen=False):
        self.x = x
        self.y = y
        self.x2 = x + width - 1
        self.y2 = y + height - 1
        self.prev_x = x
        self.prev_y = y
        self.r = int (width // 2)
        self.width = width
        self.height = height
        self.center = width // 2
        self.max_x_speed = 3
        self.max_y_speed = 3
        self.frozen = frozen
        self.tft = tft
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.x_speed2 = 0.0
        self.y_speed2 = 0.0
        self.created = ticks_ms()

    def clear(self):
        """Clear ball."""
        self.tft.circle (self.x+self.r, self.y+self.r, self.r,COLOR_BG, COLOR_BG)

    def clear_previous(self):
        """Clear prevous ball position."""
        self.tft.circle (self.prev_x+self.r, self.prev_y+self.r, self.r,COLOR_BG, COLOR_BG)

    def draw(self):
        """Draw ball."""
        self.clear_previous()
        self.tft.circle (self.x+self.r, self.y+self.r, self.r,COLOR_BALL, COLOR_BALL)

    def set_position(self, paddle_x, paddle_y, paddle_x2, paddle_center):
        bounced = False
        """Set ball position."""
        self.prev_x = self.x
        self.prev_y = self.y
        # Check if frozen to paddle
        if self.frozen:
            # Freeze ball to top center of paddle
            self.x = paddle_x + (paddle_center - self.center)
            self.y = paddle_y - self.height
            if ticks_diff(ticks_ms(), self.created) >= 2000:
                # Release frozen ball after 2 seconds
                self.frozen = False
            else:
                return
        self.x += int(self.x_speed) + int(self.x_speed2)
        self.x_speed2 -= int(self.x_speed2)
        self.x_speed2 += self.x_speed - int(self.x_speed)

        self.y += int(self.y_speed) + int(self.y_speed2)
        self.y_speed2 -= int(self.y_speed2)
        self.y_speed2 += self.y_speed - int(self.y_speed)

        # Bounces off walls
        if self.y < 10:
            self.y = 10
            self.y_speed = -self.y_speed
            bounced = True
        if self.x + self.width >= g.screenW - 5:
            self.x = g.screenW - 5 - self.width
            self.x_speed = -self.x_speed
            bounced = True
        elif self.x < 5:
            self.x = 5
            self.x_speed = -self.x_speed
            bounced = True

        # Check for collision with Paddle
        if (self.y2 >= paddle_y and
           self.x <= paddle_x2 and
           self.x2 >= paddle_x):
            # Ball bounces off paddle
            self.y = paddle_y - (self.height + 1)
            ratio = ((self.x + self.center) -
                     (paddle_x + paddle_center)) / paddle_center
            self.x_speed = ratio * self.max_x_speed
            self.y_speed = -sqrt(max(1, self.max_y_speed ** 2 - self.x_speed ** 2))
            bounced = True

        self.x2 = self.x + self.width - 1
        self.y2 = self.y + self.height - 1
        return bounced


class Brick(object):
    """Brick."""

    def __init__(self, x, y, color, tft, width=30, height=10):
        """Initialize brick.

        Args:
            x, y (int):  X,Y coordinates.
            color (string):  Blue, Green, Pink, Red or Yellow.
            tft (SSD1351): OLED g.tft.
            width (Optional int): Blick width
            height (Optional int): Blick height
        """
        self.x = x
        self.y = y
        self.x2 = x + width - 1
        self.y2 = y + height - 1
        self.center_x = x + (width // 2)
        self.center_y = y + (height // 2)
        self.color = color
        self.width = width
        self.height = height
        self.tft = tft
        self.draw()

    def bounce(self, ball_x, ball_y, ball_x2, ball_y2,
               x_speed, y_speed,
               ball_center_x, ball_center_y):
        """Determine bounce for ball collision with brick."""
        x = self.x
        y = self.y
        x2 = self.x2
        y2 = self.y2
        center_x = self.center_x
        center_y = self.center_y
        if ((ball_center_x > center_x) and
           (ball_center_y > center_y)):
            if (ball_center_x - x2) < (ball_center_y - y2):
                y_speed = -y_speed
            elif (ball_center_x - x2) > (ball_center_y - y2):
                x_speed = -x_speed
            else:
                x_speed = -x_speed
                y_speed = -y_speed
        elif ((ball_center_x > center_x) and
              (ball_center_y < center_y)):
            if (ball_center_x - x2) < -(ball_center_y - y):
                y_speed = -y_speed
            elif (ball_center_x - x2) > -(ball_center_y - y):
                x_speed = -x_speed
            else:
                x_speed = -x_speed
                y_speed = -y_speed
        elif ((ball_center_x < center_x) and
              (ball_center_y < center_y)):
            if -(ball_center_x - x) < -(ball_center_y - y):
                y_speed = -y_speed
            elif -(ball_center_x - x) > -(ball_center_y - y):
                y_speed = -y_speed
            else:
                x_speed = -x_speed
                y_speed = -y_speed
        elif ((ball_center_x < center_x) and
              (ball_center_y > center_y)):
            if -(ball_center_x - x) < (ball_center_y - y2):
                y_speed = -y_speed
            elif -(ball_center_x - x) > (ball_center_y - y2):
                x_speed = -x_speed
            else:
                x_speed = -x_speed
                y_speed = -y_speed

        return [x_speed, y_speed]

    def clear(self):
        """Clear brick."""
        self.tft.rect(self.x, self.y, self.width, self.height, COLOR_BG, COLOR_BG)

    def draw(self):
        """Draw brick."""
        self.tft.rect(self.x, self.y, self.width, self.height, COLOR_BRICK, COLOR_BRICK)


class Life(object):
    """Life."""

    def __init__(self, index, tft, width=4, height=6):
        """Initialize life.

        Args:
            index (int): Life number (1-based).
            tft (SSD1351): OLED g.tft.
            width (Optional int): Life width
            height (Optional int): Life height
        """
        margin = 10
        self.tft = tft
        self.x = g.screenW - (index * (width + margin))
        self.y = 0
        self.width = width
        self.height = height
        self.draw()

    def clear(self):
        """Clear life."""
        self.tft.rect(self.x, self.y, self.width, self.height,COLOR_BG, COLOR_BG)

    def draw(self):
        """Draw life."""
        self.tft.rect(self.x, self.y,
                                 self.width, self.height, COLOR_FG, COLOR_FG)


class Paddle(object):
    """Paddle."""

    def __init__(self, tft, width, height):
        """Initialize paddle.

        Args:
            tft (SSD1306): OLED g.tft.
            width (Optional int): Paddle width
            height (Optional int): Paddle height
        """
        self.x = 150
        self.y = 230
        self.x2 = self.x + width - 1
        self.y2 = self.y + height - 1
        self.width = width
        self.height = height
        self.center = width // 2
        self.tft = tft

    def clear(self):
        """Clear paddle."""
        self.tft.rect(self.x, self.y, self.width, self.height, COLOR_BG, COLOR_BG)


    def draw(self):
        """Draw paddle."""
        self.tft.rect(self.x, self.y,self.width, self.height, COLOR_BAT, COLOR_BAT)

    def h_position(self, x):
        """Set paddle position.

        Args:
            x (int):  X coordinate.
        """
        new_x = max(5,min (x, 320-self.width))
        if new_x != self.x :  # Check if paddle moved
            self.clear()
            self.x = new_x
            self.x2 = self.x + self.width - 1
            self.y2 = self.y + self.height - 1
            self.draw()

class Score(object):
    """Score."""

    def __init__(self, tft):
        """Initialize score.

        Args:
            tft (SSD1306): OLED g.tft.
        """
        margin = 5
        self.tft = tft
        self.tft.text( margin, 0,'S:', COLOR_MENU)
        self.x = 20 + margin
        self.y = 0
        self.value = 0
        self.draw()

    def draw(self):
        """Draw score value."""
        self.tft.rect(self.x, self.y, 20, 8, COLOR_BG, COLOR_BG)
        self.tft.text( self.x, self.y,str(self.value), COLOR_FG)

    def game_over(self):
        """Display game_over."""
        self.tft.text( (self.tft.screensize()[0] // 2) - 30,
                               int(self.tft.screensize()[1]/ 1.5),'GAME OVER', COLOR_FG)

    def increment(self, points):
        """Increase score by specified points."""
        self.value += points
        self.draw()

def load_level(level, tft) :


    bricks = []
    for row in range(fontH+2, 40 + 20 * level , 20):
        for col in range(20, g.screenW - 40, 40 ):
            bricks.append(Brick(col, row, COLOR_BRICK, tft))

    return bricks

demoOn = False
exitGame = False
while not exitGame :
    g.frameRate = 50
    paddle_width = 60
    gc.collect()
    print (gc.mem_free())


    gameOver = False
    usePaddle = False
    if demoOn :
        demo = True
    else :
        demo = False

    updateMenu = True

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


    if not exitGame :
      g.tft.clear(COLOR_BG)

      # Generate bricks
      MAX_LEVEL = const(5)
      level = 1
      bricks = load_level(level, g.tft)

      # Initialize paddle
      paddle = Paddle(g.tft, paddle_width, 3)

      # Initialize score
      score = Score(g.tft)

      # Initialize balls
      balls = []
      # Add first ball
      balls.append(Ball(150, 222, -4, -2, g.tft, frozen=True))

      # Initialize lives
      lives = []
      for i in range(1, 4):
          lives.append(Life(i, g.tft))

      prev_paddle_vect = 0

      while not gameOver :
          g.getBtn()
          if demo :
            if g.justReleased (g.btnMenu) :
              g.tft.text( 5, 30,'Demo stopped', COLOR_FG)

              sleep_ms(1000)
              gameOver = True
              demoOn = False
            else :
              paddle.h_position(balls[0].x - int(paddle_width//2) +  g.random (0,int(paddle_width * 0.6)))
          elif usePaddle :
            paddle.h_position(int(g.getPaddle() // 9.57))
          else :
            paddle_vect = 0
            if g.pressed(g.btnL | g.btnA) :
              paddle_vect = -1
            elif g.pressed(g.btnR | g.btnB) :
              paddle_vect = 1
            if paddle_vect != prev_paddle_vect :
              paddle_vect *= 5
            else :
              paddle_vect *= 10
            paddle.h_position(paddle.x + paddle_vect)
            prev_paddle_vect = paddle_vect

           # Handle balls
          score_points = 0
          for ball in balls:
              # move ball and check if bounced off walls and paddle
              if ball.set_position(paddle.x, paddle.y,paddle.x2, paddle.center):
                  g.playSound(900, 10)
              # Check for collision with bricks if not frozen
              if not ball.frozen:
                  prior_collision = False
                  ball_x = ball.x
                  ball_y = ball.y
                  ball_x2 = ball.x2
                  ball_y2 = ball.y2
                  ball_center_x = ball.x + ((ball.x2 + 1 - ball.x) // 2)
                  ball_center_y = ball.y + ((ball.y2 + 1 - ball.y) // 2)

                  # Check for hits
                  for brick in bricks:
                      if(ball_x2 >= brick.x and
                         ball_x <= brick.x2 and
                         ball_y2 >= brick.y and
                         ball_y <= brick.y2):
                          # Hit
                          if not prior_collision:
                              ball.x_speed, ball.y_speed = brick.bounce(
                                  ball.x,
                                  ball.y,
                                  ball.x2,
                                  ball.y2,
                                  ball.x_speed,
                                  ball.y_speed,
                                  ball_center_x,
                                  ball_center_y)
                              g.playTone('c6', 10)
                              prior_collision = True
                          score_points += 1
                          brick.clear()
                          bricks.remove(brick)

              # Check for missed
              if ball.y2 > g.screenH - 2:
                  ball.clear_previous()
                  balls.remove(ball)
                  if not balls:
                      # Lose life if last ball on screen
                      if len(lives) == 0:
                          score.game_over()
                          g.playTone('g4', 500)
                          g.playTone('c5', 200)
                          g.playTone('f4', 500)
                          gameOver = True
                      else:
                          # Subtract Life
                          lives.pop().clear()
                          # Add ball
                          balls.append(Ball(150, 192, 4, -6, g.tft, frozen=True))

              else:
                  # Draw ball
                  ball.draw()
          # Update score if changed
          if score_points:
              score.increment(score_points)

          # Check for level completion
          if not bricks:
              for ball in balls:
                  ball.clear()
              balls.clear()

              paddle_width = 20 if paddle_width <= 20 else paddle_width - 5
              g.frameRate = 120 if g.frameRate >= 120 else g.frameRate + 5
              level = 1 if level >= MAX_LEVEL else level + 1

              bricks = load_level(level, g.tft)
              balls.append(Ball(150, 192, -4, -2, g.tft, frozen=True))
              g.playTone('c5', 20)
              g.playTone('d5', 20)
              g.playTone('e5', 20)
              g.playTone('f5', 20)
              g.playTone('g5', 20)
              g.playTone('a5', 20)
              g.playTone('b5', 20)
              g.playTone('c6', 20)
          g.wait()

      sleep_ms(2000)
if g.ESP32 :
    g.deinit()
    del sys.modules["gameogo"]
gc.collect()
