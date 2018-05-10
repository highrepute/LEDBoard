# -*- coding: utf-8 -*-
"""
Created on Tue May  8 15:59:36 2018

@author: James.Jacobs
"""

from threading import Timer

def hello():
    print("hello, world")

t = Timer(5.0, hello)
t.start() # after 30 seconds, "hello, world" will be printed
t.cancel()
t = Timer(5.0, hello)
t.start()