# Tetriso.py
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
g.tft.set_bg(COLOR_BG)
g.tft.set_fg(COLOR_FG)
g.tft.font(g.tft.FONT_Ubuntu)

g.frameRate = 10

# size = width, height = 200, 400
size = width, height = 120, 240
COLOR_BOX = g.tft.MAROON
blockcolor =[g.tft.CYAN, g.tft.GREEN, g.tft.YELLOW, g.tft.RED, g.tft.BLUE,g.tft.PINK,g.tft.MAGENTA,g.tft.ORANGE]
sqrsize = int (width /10)
top_of_screen = (2, 2)
new_shape_x = 160
new_shape_y = 80
top_x, top_y = top_of_screen[0], top_of_screen[1]
num_block = 4
mov_delay, r_delay = 200, 50
board_centre = int(width/2)+2
no_move = 0
score = 0
life = 0
shape_blcks = []
shape_name = ""
shape_color = 0
new_shape_blcks = []
new_shape_name = ""
new_shape_color = 0
occupied_squares = []
occupied_colors = []


g.maxBgm = 3
bgmBuf= [
    [g.songStart, False, 1, g.songEnd],

    # Tetris
    [ g.songStart,False,200, 0, 4,
    659,2, 494, 1, 523,1, 587,2, 523, 1, 493, 1, 440, 2, 440, 1, 523,1, 659,2,587,1,523,1,493,2, 493,1,523,1,587,2,659,2,523,2,440,2,440,2,0,2,587, 1,698,1,880,2,783,1,698,1,659,2,523,1,659,2,587,1,523,1,493,2,493,1,523,1,587,2,659,2,523,2,440,2,440,2,0,2,
    329,4,261,4,293,4,246,4,261,4,220,4,207,4,246,4,329,4,261,4,293,4,246,4,261,2,329,2,440,4,415,6,0,2,
    g.songLoop],

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
    [ g.songStart,False, 1,  0, 400,
    440, 400, 0, 100, 440, 400, 0, 100, 440, 400, 0,100, 349, 350, 523, 150,   440, 500, 349, 350, 523, 150, 440, 650, 0,500, 659, 500, 659, 500, 659, 500,  698, 350, 523, 150, 415, 500, 349, 350, 523, 150, 440, 650, 0, 500,
    880, 500, 440, 300, 440, 150, 880, 500, 830, 325, 784, 175, 740, 125, 698, 125,  740, 250, 0, 325,  445, 250, 622, 500, 587, 325,   554, 175,   523, 125,  466, 125,   523, 250,  0, 350,
    349, 250,  415, 500, 349, 350, 440, 125, 523, 500, 440, 375,   523, 125, 659, 650, 0, 500,349, 250,  415, 500, 349, 375, 523, 125, 440, 500,  349, 375,   523, 125, 440, 650,0, 650,
    880, 500, 440, 300, 440, 150, 880, 500, 830, 325, 784, 175, 740, 125, 698, 125,  740, 250, 0, 325,  445, 250, 622, 500, 587, 325,   554, 175,   523, 125,  466, 125,   523, 250,  0, 350,
    g.songLoop]

    ]

def reset_board():
    global shape_blcks, shape_name, occupied_squares, occupied_colors
    shape_blcks = []
    shape_name = ""
    occupied_squares = []
    occupied_colors = []
    g.tft.clear(COLOR_BG)
    g.tft.rect(top_x-1, top_y-1, width+2, height+2,g.tft.RED)

def drawScore () :
  global score, life
  g.tft.text(160, 0, 'S:{}'.format (score), COLOR_FG)
  g.tft.text(240, 0, 'L:{}'.format (life),  COLOR_FG)

def draw_shape():
    '''this draws list of blocks or a block to the background and blits
    background to screen'''

    if isinstance(shape_blcks,list):
        for blck in shape_blcks:
            g.tft.rect(blck[0], blck[1], sqrsize, sqrsize, COLOR_BOX, shape_color)
    else:
        g.tft.rect(shape_blcks[0], shape_blcks[1], sqrsize, sqrsize, COLOR_BOX, shape_color)

def row_filled(row_no):
    global occupied_squares
    '''check if a row is fully occupied by a shape block'''

    for x_coord in range(top_x, width+top_x, sqrsize):

        if (x_coord, row_no) in occupied_squares:
            continue
        else:
            return False
    return True


def delete_row(row_no):

    new_sqrs = []
    new_colors = []
    x_coord, y_coord = 0, 1

    '''removes all squares on a row from the occupied_squares list and then
    moves all square positions which have y-axis coord less than row_no down
    board'''
    global occupied_squares, occupied_colors
    # erase all blocks on the screen
    for sqr in occupied_squares:
        g.tft.rect(sqr[x_coord], sqr[y_coord], sqrsize, sqrsize, COLOR_BG, COLOR_BG)


    for index in range(len(occupied_squares)):
        if occupied_squares[index][y_coord] != row_no:
            new_sqrs.append(occupied_squares[index])
            new_colors.append(occupied_colors[index])

    occupied_squares = new_sqrs
    occupied_colors = new_colors

    # adjudt the Y co-ord of the blocks below the deleted row
    for index in range(len(occupied_squares)):
        if occupied_squares[index][y_coord] < row_no:
            occupied_squares[index] = (occupied_squares[index][x_coord],
                                    occupied_squares[index][y_coord] + sqrsize)

    #redraw all the blocks
    for index in range(len(occupied_squares)):
        g.tft.rect(occupied_squares[index][x_coord], occupied_squares[index][y_coord], sqrsize, sqrsize, COLOR_BOX, occupied_colors[index])

def move(direction):
    global shape_blcks
    '''input:- list of blocks making up a tetris shape
    output:- list of blocks making up a tetris shape
    function moves the input list of blocks that make up shape and then checks
    that the  list of blocks are all in positions that are valide. position is
    valid if it has not been occupied previously and is within the tetris board.
    If move is successful, function returns the moved shape and if move is not
    possible, function returns a false'''
    directs = {'down':(no_move, sqrsize), 'left':(-sqrsize, no_move),
        'right':(sqrsize, no_move), 'pause': (no_move, no_move)}
    delta_x, delta_y = directs[direction]

    for index in range(num_block):
        shape_blcks[index] = [shape_blcks[index][0] + delta_x, shape_blcks[index][1]+ delta_y]

    if legal(shape_blcks):
        for index in range(num_block):
            #erase previous positions of block
            g.tft.rect(shape_blcks[index][0]-delta_x, shape_blcks[index][1]-delta_y, sqrsize, sqrsize, COLOR_BG, COLOR_BG)
        return True
    else:
        # undo the move, as it's not legal (being blocked by existing blocks)
        for index in range(num_block):
            shape_blcks[index] = [shape_blcks[index][0]-delta_x, shape_blcks[index][1]- delta_y]
        return False


def legal(blcks):
    '''input: list of shape blocks
    checks whether a shape is in a legal portion of the board as defined in the
    doc of 'move' function'''

    for index in range(num_block):
        new_x = blcks[index][0]
        new_y = blcks[index][1]
        if (((new_x, new_y) in occupied_squares or new_y >= height) or
            (new_x >= width or new_x < top_x)):
            return False

    return True


def create_newshape(start_x=board_centre, start_y=2):
    '''A shape is a list of four rectangular blocks.
    Input:- coordinates of board at which shape is to be created
    Output:- a list of the list of the coordinates of constituent blocks of each
    shape relative to a reference block and shape name. Reference block  has
    starting coordinates of start_x and start_y. '''
    global shape_blcks, shape_name, shape_color, new_shape_blcks, new_shape_name, new_shape_color
    shape_blcks = new_shape_blcks
    shape_name = new_shape_name
    shape_color = new_shape_color

    shape_names = ['S', 'O', 'I', 'L', 'T']
    shapes = {'S':[(start_x + 1*sqrsize, start_y + 2*sqrsize),
        (start_x, start_y), (start_x, start_y + 1*sqrsize),(start_x + 1*sqrsize,
                                                    start_y + 1*sqrsize)],

        'O':[(start_x + 1*sqrsize, start_y + 1*sqrsize), (start_x, start_y),
            (start_x, start_y + 1*sqrsize), (start_x + 1*sqrsize, start_y)],

        'I':[(start_x, start_y + 3*sqrsize), (start_x, start_y),
            (start_x, start_y + 2*sqrsize), (start_x, start_y + 1*sqrsize)],

        'L':[(start_x + 1*sqrsize, start_y + 2*sqrsize), (start_x, start_y),
            (start_x, start_y + 2*sqrsize), (start_x, start_y + 1*sqrsize)],

        'T':[(start_x + 1*sqrsize, start_y + 1*sqrsize),(start_x, start_y),
            (start_x - 1*sqrsize, start_y + 1*sqrsize),(start_x,
                                                        start_y + 1*sqrsize)]
        }
    a_shape = g.random(0, 4)

    # erase previous New_shape_block on the preview screen
    if isinstance(new_shape_blcks, list):
        for blck in new_shape_blcks:
            g.tft.rect(blck[0]+new_shape_x, blck[1]+new_shape_y, sqrsize, sqrsize, COLOR_BG, COLOR_BG)
    else:
        g.tft.rect(new_shape_blcks[0]+new_shape_x, new_shape_blcks[1]+new_shape_y, sqrsize, sqrsize,COLOR_BG, COLOR_BG)

    new_shape_blcks = shapes[shape_names[a_shape]]
    new_shape_name = shape_names[a_shape]
    new_shape_color = blockcolor[g.random(0,len(blockcolor)-1)]

    # draw New_shape_block on the preview screen
    if isinstance(new_shape_blcks, list):
        for blck in new_shape_blcks:
            g.tft.rect(blck[0]+new_shape_x, blck[1]+new_shape_y, sqrsize, sqrsize, COLOR_BOX,new_shape_color)
    else:
        g.tft.rect(new_shape_blcks[0]+new_shape_x, new_shape_blcks[1]+new_shape_y, sqrsize, sqrsize,COLOR_BOX,new_shape_Color)

def rotate():
    '''input:- list of shape blocks
    ouput:- list of shape blocks
    function tries to rotate ie change orientation of blocks in the shape
    and this applied depending on the shape for example if a 'O' shape is passed
    to this function, the same shape is returned because the orientation of such
    shape cannot be changed according to tetris rules'''
    if shape_name == 'O':
        return shape_blcks
    else:
        ref_shape_ind = 3 # index of block along which shape is rotated
        start_x, start_y = (shape_blcks[ref_shape_ind][0],
                            shape_blcks[ref_shape_ind][1])
        save_blcks = shape_blcks
        Rshape_blcks = [(start_x + start_y-shape_blcks[0][1],
                        start_y - (start_x - shape_blcks[0][0])),
        (start_x + start_y-shape_blcks[1][1],
         start_y - (start_x - shape_blcks[1][0])),
        (start_x + start_y-shape_blcks[2][1],
         start_y - (start_x - shape_blcks[2][0])),
        (shape_blcks[3][0], shape_blcks[3][1])]

        if legal(Rshape_blcks):
            for index in range(num_block): # erase the previous shape
                g.tft.rect(shape_blcks[index][0], shape_blcks[index][1],sqrsize, sqrsize, COLOR_BG, COLOR_BG)
            return Rshape_blcks
        else:
            return shape_blcks

exitGame = False
demo = False
demoOn = False

while not exitGame:
  g.startSong(bgmBuf[g.bgm])
  updateMenu = True
  gameOver = False
  #menu screen
  while True:
    if updateMenu :
        updateMenu = False

        g.tft.clear(COLOR_BG)
        g.tft.text(0,0,'Breakout', COLOR_FG)
        g.display_vol()
        g.tft.text(0,g.screenH * 1 // 7,    'A          Start',COLOR_FG)
        g.tft.text(0,g.screenH * 2 // 7,    'Menu   Quit',COLOR_FG)
        if demo :
             g.tft.text(0,g.screenH // 7 * 3,'D          AI-Player', COLOR_FG)
        else :
             g.tft.text(0,g.screenH // 7 * 3,'D          1-Player',COLOR_FG)
        g.tft.text(0,g.screenH // 7 * 4,     'Sel + U/D Frame/s {}'.format(g.frameRate), COLOR_FG)
        g.tft.text(0,g.screenH // 7 * 5,     'Vol + U/D Loudness', COLOR_FG)
        if g.bgm :
            g.tft.text(0,g.screenH // 8 * 7,'R          Background Music {}'.format(g.bgm), COLOR_FG)
        else :
            g.tft.text(0,g.screenH // 7 * 6,'R          Background Music Off', COLOR_FG)
    sleep_ms(10)
    g.getBtn()
    if g.setVol() :
         updateMenu = True
    elif g.setFrameRate():
         updateMenu = True
    elif g.justPressed(g.btnMenu) :
         exitGame = True
         gameOver= True
         g.tft.clear(COLOR_BG)
         g.center_msg(" Game Exited ",COLOR_FG, COLOR_BG)
         break
    elif g.justPressed(g.btnA) :
        if demo :
            demoOn = True
            g.tft.clear(COLOR_BG)
            g.center_msg('Menu to Stop Demo', COLOR_FG, COLOR_BG)
            sleep_ms(1000)
        break
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
    sleep_ms(10)

  if not exitGame :
    life = 3
    Score = 0
    reset_board()
    create_newshape()

  # game loop
  while not gameOver:
    drawScore()
    create_newshape()
    extramoves = 3
    l_of_blcks_ind = blck_x_axis = 0
    shape_name_ind = blck_y_axis = 1

    move_dir = 'down' #default move direction
    game = 'playing'  #default game state play:- is game paused or playing

    if legal(shape_blcks):
        draw_shape()
    else:
        g.playTone('g4', 100)
        g.playTone('e4', 100)
        g.playTone('c4', 100)
        life -= 1
        if life <= 0 :
            gameOver = True
            g.center_msg(" Game Over  ",COLOR_FG, COLOR_BG)
            sleep_ms(2000)
            break
        else :
            sleep_ms(1000)
            reset_board()
            g.bgm = 0 if g.bgm >= g.maxBgm else g.bgm + 1
            if g.bgm :
                g.startSong(bgmBuf[g.bgm])
            continue


    while True :
        mov_delay = 100
        move_dir  = 'down'
        g.getBtn()
        if game == 'paused':
            if g.justPressed(g.btnB) :
                game = 'playing'
        else:
            if g.justPressed(g.btnB) :
                game = 'paused'
                move_dir  = 'pause'
            elif g.justPressed(g.btnMenu) :
                g.center_msg(" Return to Menu  ",COLOR_FG, COLOR_BG)
                sleep_ms(1000)
                gameOver = True
                break
            elif g.pressed(g.btnD) :
                mov_delay = 10
                move_dir  = 'down'
            elif g.justPressed(g.btnA | g.btnU) :
                shape_blcks = rotate()
                draw_shape()
                sleep_ms(r_delay)
                continue
            elif g.pressed(g.btnL):
                move_dir = 'left'
                mov_delay = 50
                move (move_dir)
                draw_shape()
                sleep_ms(mov_delay)
                continue
            elif g.pressed(g.btnR):
                move_dir = 'right'
                mov_delay = 50
                move (move_dir)
                draw_shape()
                sleep_ms(mov_delay)
                continue

            moved = move( move_dir)
            draw_shape()
            sleep_ms(mov_delay)

            '''if block did not move and the direction for movement is down
            then shape has come to rest so we can exit loop and then a new
            shape is generated. if direction for movement is sideways and
            block did not move it should be moved down rather'''
            if not moved and move_dir == 'down':
              extramoves = extramoves - 1
              if extramoves <= 0 :
                for block in shape_blcks:
                    occupied_squares.append((block[0],block[1]))
                    occupied_colors.append(shape_color)
                break


            draw_shape()
#           sleep_ms(mov_delay)

            for row_no in range (height - sqrsize + top_y, 0, -sqrsize):
                if row_filled(row_no):
                    delete_row(row_no)
                    score+=10
                    drawScore()
                    g.playTone('c4', 100)
                    g.playTone('e4', 100)
                    g.playTone('g4', 100)
                    g.playTone('e4', 100)
                    g.playTone('c4', 100)
#            g.playSong()
            g.wait()

g.deinit()
del sys.modules["gameogo"]
gc.collect()
