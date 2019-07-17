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

nChannels = 4
nScans = 25
bufferSize = nScans*nChannels
on_time = 10
print("reading_buffer1=dmm.makebuffer("+str(bufferSize)+")")
my_instrument_2.write('reset()')                                                        #Reset
my_instrument_2.write("reading_buffer1=dmm.makebuffer("+str(bufferSize)+")")                            #Configure Buffer
my_instrument_2.write('dmm.func = dmm.DC_VOLTS')                                        #Set measurement function: Voltage
my_instrument_2.write('dmm.nplc=1')                                                    #The integration rate in line cycles for the DMM for the function selected by dmm.func.
my_instrument_2.write('dmm.range=10')                                                #Set Range
my_instrument_2.write('dmm.configure.set("mydcvolts")')                                #Save Configuration
my_instrument_2.write('dmm.setconfig("1001:1010","mydcvolts")')                        #Assign configuration to channels

my_instrument_2.write('scan.bypass=scan.OFF')      #Turns scan bypass off, it is on by default   #Whether the first channel of the scan waits for the channel stimulus event to be satisfied before closing.
my_instrument_2.write('scan.create("1001:1004")')                    #Create Scan
my_instrument_2.write('scan.trigger.arm.stimulus = 40')              #Which event starts the scan, 40 = trigger via GPIB, a *trg message
my_instrument_2.write("scan.scancount="+str(nScans))                 #Pass scan count from function call
my_instrument_2.write('scan.background(reading_buffer1)')            #Execute Scan

my_instrument_2.write('beeper.enable = beeper.ON')

while (nScans>0):
      
    my_instrument_2.write('*TRG')
    print(nScans)
    time.sleep(on_time)
    nScans = nScans - 1

my_instrument_2.write('beeper.beep(2, 2400)')















