# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time

from neopixel import *

TOTAL_LED_COUNT = 150
LED_CHIP_NUMBER = 0

strip = Adafruit_NeoPixel(TOTAL_LED_COUNT, 18, 800000, 5, False, 255)
strip.begin()
for i in range(0,TOTAL_LED_COUNT,1):
    strip.setPixelColorRGB(151-1, 100, 0, 0)
    strip.show()
    time.sleep(2)
