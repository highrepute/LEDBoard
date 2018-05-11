# -*- coding: utf-8 -*-
"""
Created on Tue May  8 15:59:36 2018

@author: James.Jacobs
"""

import time
from time import sleep

now = time.time()
print(now)

sleep(5)

delta = time.time() - now
print(delta)