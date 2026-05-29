"""
Created on 2 jul. 2019

@author: sansanda

requires python 3.11.6
"""

import logging
import time
import msvcrt
import pyvisa as visa
import sys
from pathlib import Path 

from utilities.csv import csv_connection as csv_connection 
from utilities.readers.file_readers import read_config_file
from utilities.readers.parameters_readers import read_time_parameters, read_current_parameters, read_gpib_addrs, \
    read_channel_parameters, read_file_parameters
from utilities.validators.valid_parameters import valid_time_parameters
from utilities.validators.validators import validate_time_parameters


SRC_ROOT = Path(__file__).resolve().parents[1]
CONTEXT_FILE = SRC_ROOT / "context3.txt"
logging.basicConfig(
    filename="powercycling.log",
    level=logging.INFO
)

config = read_config_file(CONTEXT_FILE)

time_parameters = read_time_parameters(config)
current_parameters = read_current_parameters(config)
gpib_addrs = read_gpib_addrs(config)
channel_parameters = read_channel_parameters(config)
file_parameters = read_file_parameters(config)

#Check if all the times are OK
if not validate_time_parameters(time_parameters,
                                valid_time_parameters):
    exit()    #If any mentioned fact has happened, the program exits.


#CREATE AND OPEN THE CSV FILE TO TRANSFR THE ACQUIRED DATA
field_names = ['Number of cycles', 'Semicycle']    #Create an array of constant headers
for channel in range(1, channel_parameters['number_total_channels']+1):    #Headers depend on the number of channels
    field_names.append(str(channel))   #Append the channels after the constant headers
        
csv_connection.create_csv_file(SRC_ROOT / file_parameters['csv_file_path'], field_names)    #Open the csv file and write the array of headers

#---------------------------------------------------------------------------------------------


#COUNTER OF CYCLES DONE AND A STOP BUTTON
cycle_count = 0   #Initialize the number of cycles 
stop = False    #Boolean in order to stop the electronic load whenever necessary. 


#DEFINING THE BUFFER CHARACTERISTICS
nScansPerSemicicle = 2    #Number of scans per cycle: -Measure when current is high, -Measure when current is low
#One Scan=Measure of all channels
bufferSize = nScansPerSemicicle*(channel_parameters['number_total_channels'])   #Capacity of the buffer will be the number of channels times the number of scans
#The buffer will be emptied each cycle
bufferName = "reading_buffer"

#OPENING THE RESOURCE MANAGER
rm = visa.ResourceManager()

#TAKE CONTROLLER-IN-CHARGE STATUS ON THE GPIB BUS
gpib_interface = rm.open_resource('GPIB0::INTFC')
gpib_interface.send_ifc()
gpib_interface.close()

#COMMUTICATE WITH THE ELECTRONIC LOAD 
electronic_load = rm.open_resource('GPIB0::'+str(gpib_addrs['electronic_load'])+'::INSTR')   #Assign a variable to the Electronic load by its address

#COMMUTICATE WITH KEITHLEY MULTIMETER
multimeter = rm.open_resource('GPIB0::'+str(gpib_addrs['multimeter'])+'::INSTR')   #Assign a variable to the multimeter by its address
multimeter.timeout = 15000


def safe_shutdown():
    try:
        electronic_load.write('CURR:TRIG {}'.format(current_parameters['curr_low']))    #Set current to low value
        electronic_load.write('*TRG')    #Send the trigger
        electronic_load.write('INPUT OFF')    #Impose that the instrument switch its input off
    except:
        pass


def wait(seconds):
    '''
    Waits for the given number of seconds. Returns True if the spacebar was
    pressed during the wait, False otherwise.
    '''
    end_time = time.time() + seconds
    while time.time() < end_time:
        if msvcrt.kbhit():
            if msvcrt.getch() == b' ':
                return True
        time.sleep(0.1)
    return False


#SENDING THE FIRST COMMANDS TO CONFIGURE THE ELECTRONIC LOAD
electronic_load.write('*CLS')    #Clear Status Command
electronic_load.write('*RST')    #Reset Command 
electronic_load.write('TRIG:SOUR BUS')    #Source triggeR will be send via bus
electronic_load.write('MODE:CURR')    #Set the operating mode: Current Mode (CC)
electronic_load.write('CURR:RANG {}'.format(current_parameters['current_range']))    #Low range current (0A-6A), High range current (0A-60A)
electronic_load.write('CURR:SLEW {}'.format(current_parameters['slew_rate']))    #The value of the Slew Rate in the file is imposed on the instrument
electronic_load.write('CURR {}'.format(current_parameters['curr_low']))    #The value of the low current is established on the instrument
electronic_load.write('INPUT ON')    #Switch on electronic load


#SENDING THE FIRST COMMANDS TO CONFIGURE KEITHLEY MULTIMETER
multimeter.clear()                  #GPIB Device Clear — aborts any pending scan from previous run
multimeter.write('reset()')    #Reset
multimeter.write('*CLS')            #Clear error queue and status registers
multimeter.write('errorqueue.clear()')    #Clear TSP error queue
multimeter.write('localnode.prompts = 0')    #The command messages do not generate prompts in console
multimeter.write('localnode.prompts4882 = 0')    #Disable the prompts for the GPIB

#Set voltage configuration
multimeter.write('dmm.func = dmm.DC_VOLTS')    #Set measurement function: Voltage
multimeter.write('dmm.nplc=1')    #The integration rate in line cycles for the DMM for the function selected by dmm.func.
multimeter.write('dmm.range=10')    #Set Range
multimeter.write("dmm.configure.set('mydcvolts')")    #Save Configuration
multimeter.write("dmm.setconfig('"+channel_parameters['voltage_channels_string']+"','mydcvolts')")

#Set current configuration (one voltage channel reserved to measure the current)
multimeter.write("dmm.configure.set('mycurrent')")    #Save Configuration
multimeter.write("dmm.setconfig('"+channel_parameters['current_channels_string']+"','mycurrent')")

#Set temperature configuration
multimeter.write('dmm.func = "temperature"')    #Set measurement function: Temperature
multimeter.write('dmm.transducer = dmm.TEMP_THERMOCOUPLE')    #Type of transducer: Thermocouple
multimeter.write('dmm.thermocouple = dmm.THERMOCOUPLE_K')    #Type of thermocouple: K
multimeter.write("dmm.configure.set('mythermocouple')")    #Save Configuration   
multimeter.write("dmm.setconfig('"+channel_parameters['temperature_channels_string']+"','mythermocouple')")    #Assign configuration to channels


try:

    #DEFINING PRINCIPAL FUNCTIONS
    def make_buffer(_bufferSize):
        '''
        This function creates the buffer with a certain capacity
        '''
        multimeter.write('errorqueue.clear()')    #Clear error queue before each cycle
        multimeter.write(str(bufferName)+'=dmm.makebuffer('+str(_bufferSize)+')')    #Configure the reading buffer
        multimeter.write(str(bufferName)+'.clear()')      
        
      
    def prepare_Scan(_n_total_channels, _nScansPerSemicicle):
        '''
        This function sets the number of channels and remains quiet till a trigger is sent.
        '''
        #Whether the first channel of the scan waits for the channel stimulus event to be satisfied before closing   
        multimeter.write('scan.bypass=scan.OFF')    
        
        #Creates an scan with a fixed number of voltage channels and adds a scan for the temperature channels
        multimeter.write("scan.create('"+channel_parameters['voltage_channels_string']+"','mydcvolts')")
        multimeter.write("scan.add('"+channel_parameters['temperature_channels_string']+"','mythermocouple')")
        multimeter.write("scan.add('"+channel_parameters['current_channels_string']+"','mycurrent')")
        
        #Prepares the scan to be waiting for a trigger
        multimeter.write('scan.trigger.arm.stimulus = 40')    #Which event starts the scan, 40 = trigger via GPIB, a *trg message
        multimeter.write("scan.scancount="+str(_nScansPerSemicicle))
        multimeter.write('scan.background('+str(bufferName)+')')
        
      
    def read_multimeter_buffer_and_write_to_file(_csv_file_path, _n_total_channels, _cycle_count): 
        '''
        This function acquires the stored data in the multimeter buffer and writes all the information needed to the csv file
        '''
        #ASK for the stored data (and make few superficial changes)
        try:
            acq_data = multimeter.query(
                f'printbuffer(1,{bufferSize},{bufferName})'
            ).replace("\n", "").split(",")
        except Exception as e:
            logging.error(f'Read error cycle {_cycle_count}: {e}')
            print(f"Read error: {e}")
            return

        if len(acq_data) != bufferSize:
            logging.warning(f'Cycle {_cycle_count}: expected {bufferSize} readings, got {len(acq_data)}')
            print(f"WARNING: expected {bufferSize}, got {len(acq_data)}")
            return

        print(f'Cycle {_cycle_count}:', acq_data)

        #As the acq_data contains the two scans, it has to be separated. One scan= n_channels measures
        acq_data_high = acq_data[:(_n_total_channels)]    #When current is high, one scan is made. As this scans is done first the array is divided from the index 0 to n_channels.
        acq_data_low = acq_data[(_n_total_channels):]    #When current is low, the other scans is made. 
        
        #Other values are useful to store (Number of cycles done, semicycle status, and the time stamp)
        const_high = [_cycle_count, 1]    #Both time Stamps are defined in start_scan_multimeter as global variables
        const_low = [_cycle_count, 0]
        
        #The two lists are concatenated, to write the values in the file in a easier way
        const_high.extend(acq_data_high)
        const_low.extend(acq_data_low)
       
        #WRITING THE VALUES TO THE CSV FILE
        csv_connection.insertRowInCSV(_csv_file_path, const_high)
        csv_connection.insertRowInCSV(_csv_file_path, const_low)


    #INITIAL DELAY BEFORE THE PROGRAM STARTS
    #The initial delay is created to prevent unwanted transients or similar incidents
    print(f'Waiting {time_parameters["initial_delay"]}s initial delay...')
    if wait(time_parameters['initial_delay']):
        print('STOP!!!')
        safe_shutdown()
        rm.close()
        exit()


    #MAIN CYCLE LOOP
    #To stop the program press the spacebar at any point
    while not stop:

        #=== PREPARE BUFFER AND SCAN FOR THIS CYCLE ===
        make_buffer(bufferSize)
        prepare_Scan(channel_parameters['number_total_channels'], nScansPerSemicicle)

        cycle_count = cycle_count + 1    #It increased at each rising current edge

        #=== HIGH CURRENT SEMICYCLE ===
        #Commands low>high
        electronic_load.write('CURR:TRIG {}'.format(current_parameters['curr_high']))    #Intensity value on memory, Preset
        electronic_load.write('*TRG')    #Send trigger signal

        #Wait until the measure time during the high semicycle
        if wait(time_parameters['t_measure_high']):
            stop = True
            break

        #Send trigger to multimeter to take the high current measurement
        multimeter.write('*TRG')   #This command sends the trigger to the multimeter in order to make a measure

        #Wait for the rest of the ON period
        if wait(time_parameters['t_on'] - time_parameters['t_measure_high']):
            stop = True
            break

        #=== LOW CURRENT SEMICYCLE ===
        #Commands high>low
        electronic_load.write('CURR:TRIG {}'.format(current_parameters['curr_low']))    #Intensity value on memory, Preset
        electronic_load.write('*TRG')    #Send trigger signal

        #Wait until the measure time during the low semicycle
        if wait(time_parameters['t_measure_low']):
            stop = True
            break

        #Send trigger to multimeter to take the low current measurement
        multimeter.write('*TRG')   #This command sends the trigger to the multimeter in order to make a measure

        #Wait until the data transfer time
        #That is for releasing the buffer capacity
        if wait(time_parameters['t_transfer_data'] - time_parameters['t_measure_low']):
            stop = True
            break

        #=== DATA TRANSFER ===
        #Read the buffer and write the data to the CSV file
        read_multimeter_buffer_and_write_to_file(
            SRC_ROOT / file_parameters['csv_file_path'],
            channel_parameters['number_total_channels'],
            cycle_count
        )

        #Wait for the rest of the OFF period
        if wait(time_parameters['t_off'] - time_parameters['t_transfer_data']):
            stop = True
            break


    #STOP REQUESTED — SAFE SHUTDOWN
    print('STOP!!!')
    logging.info(f'Test stopped by user after {cycle_count} cycles')
    safe_shutdown()
    multimeter.write('reset()')
    rm.close()


except visa.VisaIOError as e:

    logging.error(e.description)
    logging.error(e.args)
    
    print("HOlaaaa VISA ERROR")
    print(e.args)

    # Safe shutdown
    try:
        electronic_load.write('INPUT OFF')
        print("Electronic load disabled")
    except Exception as shutdown_error:
        print("Unable to disable electronic load")
        print(shutdown_error)

except Exception as e:

    logging.error(f'Unhandled exception: {e}')
    print(e)
    safe_shutdown()