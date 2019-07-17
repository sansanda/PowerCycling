'''
Created on 2 jul. 2019

@author: mespower
'''

                                #POWER CYCLING SCRIPT

import visa
import threading 
import sys
import time
import csv_connection
from tkinter import messagebox
import gc


#DEFINING A COUNTER OF CYCLES DONE AND A STOP BUTTON
cycle_count = 0   #Initialize the number of cycles 
stop = 0    #Boolean in order to stop the electronic load whenever necessary. 
T_OFF_MIN = 2
T_MEASURE_LOW_MIN = 0.5
T_TRANSFER_DATA_MIN = 1.5
T_ON_MIN = 1
T_MEASURE_HIGH_MIN = 0.5


#OPEN THE FILE THAT CONTAINS THE INITIALS VALUES
initial_values_f  = open('.\config_files\initial_values_file.txt', "r")    #Opening the file with a relative path, as readers ('r')
initial_values = initial_values_f.readlines()    #Read the open file: it will be an array of strings

for line in initial_values:   #line will be each string in the previous array 
    #Need to connect each variable with the one in the file, and use the number
    #The file configuration is: NAME_VARIABLE:VALUE
    #In order to find the values, we memorize all the characters after the index of the ':'
    if 'curr_low' in line:    #Search where is curr_low in the file, just in case the order of the values changes
        curr_low = int(line[line.index(':')+1:])    #Impose the value of the low current level
        print('Current low is:', curr_low, 'A')
    if 'curr_high' in line:
        curr_high = int(line[line.index(':')+1:])   #Impose the value of the high current level
        print('Current high is:', curr_high, 'A')
    if 'sr' in line:
        sr = float(line[line.index(':')+1:])    #Slew rate
        print('Slew Rate is:', sr) 
    if 't_on' in line:
        t_on = float(line[line.index(':')+1:])    #Set up the seconds when the electronic load is conducting
        print('Time on:', t_on, 's')
    if 't_off' in line:
        t_off = float(line[line.index(':')+1:])   #Set up the seconds when the electronic load is conducting
        print('Time off:', t_off, 's')
    if 'initial_delay' in line:
        initial_delay = float(line[line.index(':')+1:])   #Initial time, where the current is in its lower value.
        print('Initial delay is:', initial_delay, 's')
    if 't_measure_high' in line:
        t_measure_high = float(line[line.index(':')+1:])   #The seconds elapsed from the electronic load starts conducting till the multimeter measures. 
        print('Measure time on is:', t_measure_high, 's')
    if 't_measure_low' in line:
        t_measure_low = float(line[line.index(':')+1:])   #The seconds elapsed from the electronic load starts conducting till the multimeter measures. 
        print('Measure time off is:', t_measure_low, 's')
    if 'n_channels' in line:
        n_channels = int(line[line.index(':')+1:])     #Multimeter number of channels that will be measuring  
        print('Number of channels:', n_channels)
    if 't_transfer_data' in line:
        t_transfer_data = float(line[line.index(':')+1:])     #Multimeter number of channels that will be measuring  
        print('Moment to transfer the data (high and low measure):', t_transfer_data, 's')
    if 'csv_file_path' in line:
        csv_file_path = line[line.index(':')+1:]    #Relative Path to the CSV file (results)
        print('File path:', csv_file_path)
print('\n---------------------------------------------------------------')    
initial_values_f.close()    #In order to avoid errors, the file is closed



def check_time_parameters(_t_on, _t_off, _t_measure_high, _t_measure_low, _t_transfer_data):    
    
    error = False
    
    if _t_on < T_ON_MIN:
        error = True
        messagebox.showerror(message="t_on must be bigger than"+str(T_ON_MIN), title="Time Definition Error")
    if _t_off < T_OFF_MIN:
        error = True
        messagebox.showerror(message="t_off must be bigger than"+str(T_OFF_MIN), title="Time Definition Error")
    if _t_measure_high < T_MEASURE_HIGH_MIN:
        error = True
        messagebox.showerror(message="t_measure_high must be bigger than"+str(T_MEASURE_HIGH_MIN), title="Time Definition Error")   
    if _t_measure_low < T_MEASURE_LOW_MIN:
        error = True
        messagebox.showerror(message="t_measure_low must be bigger than"+str(T_MEASURE_LOW_MIN), title="Time Definition Error")  
    if _t_transfer_data < T_TRANSFER_DATA_MIN:
        error = True
        messagebox.showerror(message="t_transfer_data must be bigger than"+str(T_TRANSFER_DATA_MIN), title="Time Definition Error")  
    if t_on < t_measure_high:
        error = True
        messagebox.showerror(message="t_on must be bigger than t_measure_high", title="Time Definition Error")  
    if t_off < t_measure_low:
        error = True
        messagebox.showerror(message="t_off must be bigger than t_measure_low", title="Time Definition Error")  
    if t_off < t_transfer_data:
        error = True
        messagebox.showerror(message="t_off must be bigger than t_transfer_data", title="Time Definition Error")  
    if t_transfer_data < t_measure_low:
        error = True
        messagebox.showerror(message="t_transfer_data must be bigger than t_measure_low", title="Time Definition Error")
    if t_on<0 or t_off<0 or t_measure_high<0 or t_measure_low<0 or t_transfer_data<0:
        error = True
        messagebox.showerror(message="Times must be positive", title="Time Definition Error")
    
    return error

if check_time_parameters(t_on, t_off, t_measure_high, t_measure_low, t_transfer_data)==True:
    exit()



#DEFINING THE BUFFER SIZE AND NAME
nScansPerSemicicle = 2    
bufferSize = nScansPerSemicicle*n_channels
bufferName = "reading_buffer"

tStamps_High = 0
tStamps_Low = 0


#OPENING THE RESOURCE MANAGER
rm = visa.ResourceManager()
rm.ignore_warning()

#COMMUTICATE WITH THE ELECTRONIC LOAD 
electronic_load = rm.open_resource('GPIB0::5::INSTR')   #Assign a variable to the Electronic load by its address

#COMMUTICATE WITH KEITHLEY MULTIMETER
multimeter = rm.open_resource('GPIB0::25::INSTR')   #Assign a variable to the multimeter by its address


#SENDING THE FIRST COMMANDS TO CONFIGURE THE ELECTRONIC LOAD
electronic_load.write('*CLS')    #Clear Status Command
electronic_load.write('*RST')    #Reset Command 
electronic_load.write('TRIG:SOUR BUS')    #Source trigger
electronic_load.write('MODE:CURR')    #Set the operating mode: Current Mode (CC)
electronic_load.write('CURR:RANG 1')    #Low range current (0A-6A)
electronic_load.write('CURR:SLEW {}'.format(sr))    #The value of the Slew Rate in the file is imposed on the instrument 
electronic_load.write('CURR {}'.format(curr_low))    #The value of the low current is established on the instrument
electronic_load.write('INPUT ON')    #Switch on electronic load



#SENDING THE FIRST COMMANDS TO CONFIGURE KEITHLEY MULTIMETER
multimeter.write('reset()')    #Reset
multimeter.write('localnode.prompts = 0')    #The command messages do not generate prompts.
multimeter.write('localnode.prompts4882 = 0')    #Disable the prompts for the GPIB

multimeter.write('dmm.func = dmm.DC_VOLTS')    #Set measurement function: Voltage
multimeter.write('dmm.nplc=1')    #The integration rate in line cycles for the DMM for the function selected by dmm.func.
multimeter.write('dmm.range=10')    #Set Range
multimeter.write('dmm.configure.set("mydcvolts")')    #Save Configuration
#print("dmm.setconfig('1001:10"+str(nChannelsPerScan).zfill(2)+"','mydcvolts')")
multimeter.write("dmm.setconfig('1001:10"+str(n_channels).zfill(2)+"','mydcvolts')")    #Assign configuration to channels



#CREATE AND OPEN THE CSV FILE TO TRANSFR THE ACQUIRED DATA
field_names = ['Number of cycles', 'Semicycle', 'Time Stamp']    #First and constant headers
for channel in range(1, n_channels+1):    #Headers that depend on the number of channels
    field_names.append(str(channel))   #Append the channels after the constant headers
        
csv_connection.create_csv_file(csv_file_path, field_names)

        
        
#DEFINING FUNCTION
      
            
def make_buffer(_bufferSize):
    multimeter.write(str(bufferName)+'=dmm.makebuffer('+str(_bufferSize)+')')        # configure reading buffer
    multimeter.write(str(bufferName)+'.clear()')        # configure reading buffer
    
  
def prepare_Scan(_nChannelsPerScan,_nScansPerSemicicle):
    '''
    This function creates a buffer, sets the number of channels of the multimeter and remains quiet 
    till a trigger is sent.
    '''
       
    multimeter.write('scan.bypass=scan.OFF') 
    multimeter.write("scan.create('1001:10"+str(_nChannelsPerScan).zfill(2)+"')")
    
    multimeter.write('scan.trigger.arm.stimulus = 40')    #Which event starts the scan, 40 = trigger via GPIB, a *trg message
    multimeter.write("scan.scancount="+str(_nScansPerSemicicle))
    multimeter.write('scan.background('+str(bufferName)+')')
    
    
    
def start_scan_multimeter(_semicicle):
    '''
    This function sends the trigger to the Keithley Multimeter in order to make the measures
    in a predetermined time
    '''
    multimeter.write('*TRG')   #This command sends 
    #Two measures per cycle will be done: in the lower value of the current and in the higher value, at controlled times
    if (_semicicle==0): 
        global tStamps_Low
        tStamps_Low = time.time_ns()
    if (_semicicle==1): 
        global tStamps_High
        tStamps_High = time.time_ns()
     
   
    
def read_multimeter_buffer_and_write_to_file(_csv_file_path, _n_channels, _cycle_count): 
    
    acq_data = multimeter.query('printbuffer(1,'+str(bufferSize)+','+str(bufferName)+')').replace("\n","").split(",")
    print('Cycle {}:'.format(cycle_count), acq_data)
    acq_data_high = acq_data[:_n_channels]
    acq_data_low = acq_data[_n_channels:]
    const_high = [_cycle_count, 1, tStamps_High]
    const_low = [_cycle_count, 0, tStamps_Low]
    const_high.extend(acq_data_high)
    const_low.extend(acq_data_low)
   
    csv_connection.insertRowInCSV(_csv_file_path,const_high)
    csv_connection.insertRowInCSV(_csv_file_path,const_low)
    
def trg_up(_curr_low,_curr_high, _t_on, _t_off, _t_measure_high, _t_measure_low, _t_transfer_data):
    '''
    This function sends triggers to the electronic load in order to rise the current from the lower 
    value to the high value. Then the current remains in the higher state until the time is finished.
    It will be continuously running, unless the stop button is pulsed. Moreover, in a chosen time, 
    the function 'send trigger' is called, so the measures corresponding to 1 scan, will be registered.
    '''
    
    #Timers
    #Configure a timer is started because when the _t_on finishes, the function trg_down will be called
    timer_on = threading.Timer(_t_on, trg_down, [_curr_low,_curr_high, _t_on, _t_off, _t_measure_high, _t_measure_low,_t_transfer_data])

    #Configure another timer to claim that the measures will be done at a chosen time: t_measure_high, when the current is high.
    timer_measure_high = threading.Timer(_t_measure_high, start_scan_multimeter,[1])
        
    if stop == 0: #Nobody has pressed the stop button 
                
        make_buffer(bufferSize)
        prepare_Scan(n_channels,nScansPerSemicicle)
              
        global cycle_count    #As cycle_count is not an argument of the function, the variable must be global
        cycle_count = cycle_count + 1    #It increased at each rising current edge 
        #Commands  low>high
        electronic_load.write('CURR:TRIG {}'.format(_curr_high))    #Intensity value on memory, Preset
        electronic_load.write('*TRG')    #Send trigger signal
        
        #Start the timers
        timer_on.start()     
        timer_measure_high.start()
        
    if stop == 1:
        
        print("CANCELLING THE PROCESS!!!!!!!")
        print("CANCELLING THE PROCESS!!!!!!!")
        print("CANCELLING THE PROCESS!!!!!!!")
        
        timer_on.cancel()
        timer_on = None
        timer_measure_high.cancel()
        timer_measure_high = None
        
        
    

def trg_down(_curr_low,_curr_high, _t_on, _t_off, _t_measure_high, _t_measure_low, _t_transfer_data):
    '''
    This function sends triggers to the electronic load in order to come down the current from the high 
    value to the low value. Then the current remains in the lower state until the time is finished.
    It will be continuously running, unless the stop button is pulsed. Moreover, in a chosen time, 
    the function 'send trigger' is called, so the measures corresponding to 1 scan, will be registered.
    '''
    
    #Timers
    timer_off = threading.Timer(_t_off, trg_up, [_curr_low,_curr_high, _t_on, _t_off, _t_measure_high, _t_measure_low, _t_transfer_data])
    #A timer is started because when the _t_off finishes, the function trg_up will be call again, for ever and ever
  
    timer_measure_low = threading.Timer(_t_measure_low, start_scan_multimeter,[0])
    #Another timer to claim that the measures will be done at a chosen time: t_measure_on, when the current is low.
  
    timer_transfer = threading.Timer(_t_transfer_data, read_multimeter_buffer_and_write_to_file, [csv_file_path, n_channels, cycle_count])

  
    if stop == 0:
                
        #Commands
        electronic_load.write('CURR:TRIG {}'.format(_curr_low))    #Intensity value on memory, Preset
        electronic_load.write('*TRG')    #Send trigger signal
       
        #Start the timers
        timer_off.start() 
        timer_measure_low.start()
        timer_transfer.start()
        
    if stop == 1:
        
        print("CANCELLING THE PROCESS!!!!!!!")
        print("CANCELLING THE PROCESS!!!!!!!")
        print("CANCELLING THE PROCESS!!!!!!!")
        
        timer_off.cancel()
        timer_off = None
        timer_measure_low.cancel()
        timer_measure_low = None
        timer_transfer.cancel()
        timer_transfer = None
        



def emergency_stop():
    """
    Detects the space bar key pressed on the console, and stops the electronic load, 
    setting the current value to zero immediately.
    """
    if sys.stdin.read(1) == ' ':    #Detects when the space bar is pressed
        print('STOP')
        global stop
        stop = 1    #'trg_up'and'trg_down' will stop executing
        
        electronic_load.write('CURR:TRIG 0')    #Intensity value ZERO on memory, Preset
        electronic_load.write('*TRG')    #Send the trigger
        
        electronic_load.write('INPUT OFF')    #Impose that the instrument switch its input off
        multimeter.write('reset()')
        
        global rm
        rm.close()
        rm = None
        #gc.collect()
        
    #To stop the program 'space bar' and then 'enter' must be pressed in the console!  
        


#TIMER WITH A INITIAL DELAY TO START THE PROGRAM   
timer_initial = threading.Timer(initial_delay, trg_up, [curr_low, curr_high, t_on, t_off, t_measure_high, t_measure_low, t_transfer_data]) 
#The initial timer is created to prevent unwanted transients or similar incidents
#It allows the trg_up function to start running 
timer_initial.start()    #The timer is started 


#OPEN A THREAD TO ALLOW THE STOP BUTTON TO RUN IN PARALEL THE CODE
stop_thread = threading.Thread(target=emergency_stop())
#It is continually running independently the other code, so whenever the space bar is pressed, it will be registered
stop_thread.start()    #The thread is initialized


