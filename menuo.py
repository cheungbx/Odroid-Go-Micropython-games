# menuo.py.
# startup menu and launcher for other python programs
#
# Use common game module "gameogo.py" for ESP32 Odroid Go
# by Billy Cheung  2019 10 26

import os
import sys
import gc
gc.collect()
print (gc.mem_free())
from machine import Pin, ADC
from utime import sleep_ms, ticks_ms, ticks_diff
module_name = ""
tone_dur = 10

def do_menu (g) :
  global module_name, vol, max_vol

  # all dislplay, buttons, paddle, sound logics are in game8266.mpy module


  SKIP_NAMES = ("boot", "main", "menu","gameogo")


  files = [item[0] for item in os.ilistdir(".") if item[1] == 0x8000]


  module_names = [
      filename.rsplit(".", 1)[0]
      for filename in files
      if (filename.endswith(".py") or  filename.endswith(".mpy") ) and not filename.startswith("_")
  ]
  module_names = [module_name for module_name in module_names if not module_name in SKIP_NAMES]
  module_names.sort()
  tot_file = len(module_names)
  COLOR_FG = g.tft.GREEN
  COLOR_BG = g.tft.BLACK
  COLOR_HH = g.tft.RED
  g.tft.font(g.tft.FONT_Ubuntu)
  fontW, fontH = g.tft.fontSize()
  rowH = fontH + 2
  tot_rows = g.screenH // rowH  - 1
  screen_pos = 0
  file_pos = 0
  updateMenu = True
  launched = False
  while not launched :
    gc.collect()
    g.getBtn()
    g.setVol()

    if updateMenu :
        updateMenu = False
        g.tft.clear(g.tft.BLACK)
        g.tft.set_bg(COLOR_BG)
        g.tft.text(0, 0,'M:{}'.format(gc.mem_free()),  g.tft.RED)
        g.display_vol()
        i = 0
        for j in range (file_pos, min(file_pos+tot_rows, tot_file)) :
          if i == screen_pos :
             g.display_msg(0, rowH * (i+1), str(j) + " " + module_names[j],COLOR_FG,COLOR_HH)
          else :
             g.display_msg(0, rowH * (i+1), str(j) + " " + module_names[j],COLOR_FG,COLOR_BG)
          i+=1

    if g.justPressed(g.btnU):
        if screen_pos > 0 :
            g.display_msg(0, rowH * (screen_pos+1), str(file_pos + screen_pos) + " " + module_names[file_pos + screen_pos],COLOR_FG, COLOR_BG)
            screen_pos -= 1
            g.display_msg(0, rowH * (screen_pos+1), str(file_pos + screen_pos) + " " + module_names[file_pos + screen_pos],COLOR_FG, COLOR_HH)

        else :
            if file_pos > 0 :
                file_pos = max (0, file_pos - tot_rows)
                screen_pos=tot_rows-1
                updateMenu = True
        g.playTone('c4', tone_dur)

    if g.justPressed(g.btnD):
        if screen_pos < min(tot_file - file_pos - 1, tot_rows -1) :
            g.display_msg(0, rowH * (screen_pos+1), str(file_pos + screen_pos) + " " + module_names[file_pos + screen_pos],COLOR_FG, COLOR_BG)
            screen_pos = min(tot_file-1, screen_pos + 1)
            g.display_msg(0, rowH * (screen_pos+1), str(file_pos + screen_pos) + " " + module_names[file_pos + screen_pos],COLOR_FG, COLOR_HH)
        else :
            if file_pos + tot_rows < tot_file :
              file_pos = min (tot_file, file_pos + tot_rows)
              screen_pos=0
              updateMenu = True
        g.playTone('e4', tone_dur)


    if g.justReleased(g.btnA):
        g.playTone('c5', tone_dur)
        g.tft.clear(g.tft.BLACK)
        g.center_msg ("launching {}".format(module_names[file_pos + screen_pos]) ,COLOR_FG, COLOR_BG)
        sleep_ms(1000)
        module_name = module_names[file_pos + screen_pos]
        return True

    if g.justReleased(g.btnL):
        g.playTone('d5', tone_dur)
        launched = True
        g.tft.clear(g.tft.BLACK)
        g.center_msg ("Exited",COLOR_FG, COLOR_BG)
        return False
    sleep_ms(10)


go_on = True
from gameogo import gameOGO
g=gameOGO(False)
while go_on :

  go_on = do_menu(g)
  g.deinit()
  del sys.modules["gameogo"]

  if go_on :
    gc.collect()
    module = __import__(module_name)
    del sys.modules[module_name]
    gc.collect()


  from gameogo import gameOGO
  g=gameOGO()
