import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from const import const
import led_client


def light_problem(start_holds, prob_holds, fin_holds):
    if const.LINUX != 1:
        return
    led_client.light_problem(start_holds, prob_holds, fin_holds, source='flask')


def off():
    if const.LINUX != 1:
        return
    led_client.off(source='flask')
