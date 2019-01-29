#!/usr/bin/env python


import RPi.GPIO as GPIO
import subprocess
from neopixel import *

GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.wait_for_edge(3, GPIO.FALLING)
strip = Adafruit_NeoPixel(200, 18, 800000, 5, False, 255)
strip.begin()
strip.setPixelColorRGB(200, 0, 0, 0)
strip.show()
#subprocess.call(['shutdown', '-h', 'now'], shell=False)
