# Odroid-Go-Micropython-games
# Ported the simple game module from 8266 to Odroid-go
# Odroid-go has the ili9341 color TFT 320x240 display , plus buttons running on an ESP32 with PSRam of 4MB and Flash of 16MB
# I am using a homemade Odroid-go to test this. But these libraries works for the official Odroid-go too.
# The official Odroid-go's python libraries uses a python source code version of ili9341 drive which is too slow for games
# I created the gameogo.py to call the ili9341 drivers (written in c which is much faster) 
# from the Lobo version of Micropython for ESP32 instread.
# Note the Lobo version of Miropython for ESP32 is the default micropython build for the Odroid-Go
# You can follow the instructions on the Odroid-Go Wiki to load micropython firmware to your Odroid-go
# https://wiki.odroid.com/odroid_go/micropython/01_micropython_setup
# Then copy my gameogo.py file on to /pyboard/flash
# Then develop your game program based on these libraries.
# see invadero.py or snakeo.py or breakouto.py or pongo.py as examples
#
# usage:
# from gameogo import *
# g=gameOGO()
# follow by your game logics (see the example game source code).

