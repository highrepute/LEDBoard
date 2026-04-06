import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from const import const

_strip = None


def init_strip():
    global _strip
    if const.LINUX != 1:
        return
    try:
        from rpi_ws281x import PixelStrip
        _strip = PixelStrip(const.TOTAL_LED_COUNT, 18, 800000, 5, False, 255)
    except ImportError:
        from neopixel import Adafruit_NeoPixel
        _strip = Adafruit_NeoPixel(const.TOTAL_LED_COUNT, 18, 800000, 5, False, 255)
    _strip.begin()
    _strip.setPixelColorRGB(const.TOTAL_LED_COUNT, 0, 0, 0)
    _strip.show()


def light_problem(start_holds, prob_holds, fin_holds):
    """Light up holds for a problem. Green=start, Blue=problem, Red=finish.
    Hold IDs are 1-indexed. -1 indicates an empty hold slot (filtered out).
    """
    if const.LINUX != 1:
        return
    if _strip is None:
        init_strip()
    if _strip is None:
        return
    v = const.LED_VALUE
    for i in range(const.TOTAL_LED_COUNT):
        _strip.setPixelColorRGB(i, 0, 0, 0)
    for h in start_holds:
        if h > 0:
            _strip.setPixelColorRGB(h - 1, 0, v, 0)
    for h in prob_holds:
        if h > 0:
            _strip.setPixelColorRGB(h - 1, 0, 0, v)
    for h in fin_holds:
        if h > 0:
            _strip.setPixelColorRGB(h - 1, v, 0, 0)
    _strip.show()


def off():
    if const.LINUX != 1:
        return
    if _strip is None:
        init_strip()
    if _strip is None:
        return
    for i in range(const.TOTAL_LED_COUNT):
        _strip.setPixelColorRGB(i, 0, 0, 0)
    _strip.show()
