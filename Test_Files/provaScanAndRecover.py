'''
Created on 2 jul. 2019

@author: mespower
'''

                                #POWER CYCLING SCRIPT

import visa
import threading 
import sys
import time
from sqlite3 import Time

nScansPerSemicicle=1
nSemicicles = 10
nChannelsPerScan = 10

def makeBufferAndPrepareScan(_nChannelsPerScan,_nScansPerSemicicle):
    multimeter.write('reading_buffer=dmm.makebuffer('+str(_nChannelsPerScan)+')')        # configure reading buffer
    multimeter.write('reading_buffer.clear()')        # configure reading buffer
    
    multimeter.write('scan.bypass=scan.OFF') 
    multimeter.write("scan.create('1001:10"+str(_nChannelsPerScan).zfill(2)+"')")
    
    multimeter.write('scan.trigger.arm.stimulus = 40')    #Which event starts the scan, 40 = trigger via GPIB, a *trg message
    multimeter.write("scan.scancount="+str(_nScansPerSemicicle))
    multimeter.write('scan.background(reading_buffer)')

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

multimeter.write('dmm.func = dmm.DC_VOLTS')                    # set dmm function
multimeter.write('dmm.nplc=1')          
multimeter.write('dmm.range=10')                            # set range
multimeter.write('dmm.configure.set("mydcvolts")')    #Save Configuration
multimeter.write('dmm.setconfig("1001:1010","mydcvolts")')    #Assign configuration to channels



while (nSemicicles>0):
    makeBufferAndPrepareScan(nChannelsPerScan,nScansPerSemicicle)
    print('hola')
    print(nSemicicles)
    multimeter.write('*TRG')
    nSemicicles = nSemicicles - 1
    time.sleep(1)
    r_ = multimeter.query('printbuffer(1, 10, reading_buffer)').split(",")
    print(r_)
    
    
print('fora')

#multimeter.close()