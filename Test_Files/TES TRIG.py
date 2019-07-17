'''
Created on 5 jul. 2019

@author: mespower
'''

import visa
import threading 
import sys
import time
from threading import Thread



#COMMUTICATE WITH THE KEITHLEY MULTIMETER
rm = visa.ResourceManager()
print('Resource Manager: ', rm)
print(rm.list_resources())

my_instrument_2 = rm.open_resource('GPIB0::25::INSTR')
print('Keithley: ', my_instrument_2)

my_instrument_2.write('localnode.reset()')
my_instrument_2.write('localnode.prompts4882 = 1')


my_instrument_2.write('digio.trigger[1].clear()')
my_instrument_2.write('digio.trigger[1].mode = digio.TRIG_FALLING')
my_instrument_2.write('digio.trigger[1].pulsewidth = 100*1e-1')
my_instrument_2.write('digio.trigger[1].assert()')


    