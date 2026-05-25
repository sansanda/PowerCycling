"""
Created on 25 May. 2026

@author: sansanda

requires python 3.11.6
"""

import threading

print(threading.Thread)
print(dir(threading.Thread))

t = threading.Timer(1, lambda: print("OK"))

print(dir(t))

t.start()