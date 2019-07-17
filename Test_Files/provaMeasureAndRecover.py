'''
Created on 2 jul. 2019

@author: mespower
'''

                                #POWER CYCLING SCRIPT

import visa
import threading 
import sys
import time


#COMMUTICATE WITH THE ELECTRONIC LOAD 

rm = visa.ResourceManager()
print(rm)
print(rm.list_resources())
electronic_load = rm.open_resource('GPIB0::5::INSTR')   #Assign a variable to the Electronic load by its address
print(electronic_load)



#COMMUTICATE WITH KEITHLEY MULTIMETER
multimeter = rm.open_resource('GPIB0::25::INSTR')   #Assign a variable to the multimeter by its address
multimeter.timeout = 100000; #sets the timeout at 100s (100.000 ms)

print('Keithley: ', multimeter)
print(multimeter.query("*IDN?"))

multimeter.write('reset()')  # reset
multimeter.write('localnode.prompts = 0')
multimeter.write('localnode.prompts4882 = 0')

multimeter.write('reading_buffer=dmm.makebuffer(100)')        # configure reading buffer
multimeter.write('dmm.func = dmm.DC_VOLTS')                    # set dmm function
multimeter.write('dmm.nplc=1')          
multimeter.write('dmm.range=10')                            # set range
multimeter.write('dmm.measurecount=100')                        # set measure count
multimeter.write('dmm.measure(reading_buffer)')                # trigger measure and store reading in buffer


#multimeter.write('print(printbuffer(1,5, reading_buffer))')    # print buffer
r = multimeter.query('printbuffer(1, 100, reading_buffer)').split(",")
print(r)

#multimeter.write("reading_buffer1=dmm.makebuffer(20)")
#multimeter.write("size, cap= dmm.buffer.info('reading_buffer1')")
#r = multimeter.query("print(reading_buffer1)")
#print(r)

