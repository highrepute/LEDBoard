# -*- coding: utf-8 -*-
"""
Created on Tue May  8 15:59:36 2018

@author: James.Jacobs
"""

from collections import Counter

z = ['blue', 'red', 'blue', 'yellow', 'blue', 'red']
maxOccur = Counter(z).most_common(6)
for name,count, in maxOccur:
    print(name, count)