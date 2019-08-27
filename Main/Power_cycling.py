'''
Created on 2 jul. 2019

@author: mespower
'''
# if __name__ == '__main__':
#     pass


                                #POWER CYCLING SCRIPT

import visa
import threading 
import sys
import csv_connection
from tkinter import messagebox


#DEFINING TIME CONSTANTS
T_OFF_MIN = 2
T_MEASURE_LOW_MIN = 0.5
T_TRANSFER_DATA_MIN = 1.5
T_ON_MIN = 1
T_MEASURE_HIGH_MIN = 0.5


#OPEN THE FILE THAT CONTAINS THE INITIALS VALUES
initial_values_f  = open('.\config_files\initial_values_file.txt', "r")    #Opening the file with a relative path, as readers ('r')
initial_values = initial_values_f.readlines()    #Read the file: Array of strings

for line in initial_values:   #line: each string in the previous array 
    #Define the file variables in the script
    #The file configuration is: VARIABLE=VALUE
    #In order to find the values, we memorize all the characters after the index of the '='
    if  line.startswith("*"):   #To comment something in the file write: *
        print('Skipping comment:')
        continue
    if 'Current low' in line:    #Search where is curr_low in the file, just in case the order of the values changes
        curr_low = float(line[line.index('=')+1:])    #Impose the value of the low current level
        print('Current low is:', curr_low, 'A')
    if 'Current high' in line:
        curr_high = float(line[line.index('=')+1:])   #Impose the value of the high current level
        print('Current high is:', curr_high, 'A')
    if 'Slew Rate' in line:
        sr = float(line[line.index('=')+1:])    #Slew rate
        print('Slew Rate is:', sr) 
    if 'Time on' in line:
        t_on = float(line[line.index('=')+1:])    #Set up the seconds when the electronic load is conducting
        print('Time on:', t_on, 's')
    if 'Time off' in line:
        t_off = float(line[line.index('=')+1:])   #Set up the seconds when the electronic load is NOT conducting
        print('Time off:', t_off, 's')
    if 'Initial delay' in line:
        initial_delay = float(line[line.index('=')+1:])   #Initial time, where the current is in its lower value.
        print('Initial delay is:', initial_delay, 's')
    if 'Time measure high' in line:
        t_measure_high = float(line[line.index('=')+1:])   #The seconds elapsed from the electronic load starts conducting till the multimeter measures. 
        print('Measure time on is:', t_measure_high, 's')
    if 'Time measure low' in line:
        t_measure_low = float(line[line.index('=')+1:])   #The seconds elapsed from the electronic load starts NOT conducting till the multimeter measures. 
        print('Measure time off is:', t_measure_low, 's')
    if 'Number voltage channels' in line:
        n_channels_volt = line[line.index('=')+1:]     #Multimeter number of channels that will be measuring the voltage
        print('Number of voltage channels:', n_channels_volt)
    if 'Number temperature channels' in line:
        n_channels_temp = line[line.index('=')+1:]     #Multimeter number of channels that will be measuring the temperature
        print('Number of temperature channels:', n_channels_temp)
    if 'Voltage channels' in line:
        voltageChannelsString = str(line[line.index('=')+1:]).replace("\n",'')     #Finds the string corresponding to the voltage channels and the number
        print('Total number of voltage channels:', voltageChannelsString)          #.replace because the split introduce a new line after the match 
        _channels = voltageChannelsString.split(":", -1)
        nVoltageChannels = int(_channels[1]) - int(_channels[0]) + 1
    if 'Temperature channels' in line:
        temperatureChannelsString = str(line[line.index('=')+1:]).replace("\n",'')     #Now, in the case of temperature
        print('Total number of temperature channels:', temperatureChannelsString)    #String similar to 1001:1012
        _channels = temperatureChannelsString.split(":", -1)    #Divide the string into: 1001 and 1012
        nTemperatureChannels = int(_channels[1]) - int(_channels[0]) + 1    #Substract the two values in order to have the total number of temperature channels    
    if 'Current channel' in line:
        currentChannelsString = str(line[line.index('=')+1:]).replace("\n",'')     #Now, in the case of current
        print('Total number of current channels:', currentChannelsString)    #String similar to 1001:1001
        _channels = currentChannelsString.split(":", -1)    #Divide the string into: 1001 and 1012
        nCurrentChannels = int(_channels[1]) - int(_channels[0]) + 1    #Substract the two values in order to have the total number of temperature channels
    if 'Time transfer data' in line:
        t_transfer_data = float(line[line.index('=')+1:])     #The seconds elapsed from the electronic load starts NOT conducting till the data is transfered
        print('Moment to transfer the data (high and low measure):', t_transfer_data, 's')
    if 'Current Range' in line:
        curr_rang = float(line[line.index('=')+1:])     #Set the desired current range (LOW (0-6A) or HIGH(0-60A))
        print('Current Rang:', curr_rang, 'A')
    if 'Csv file path' in line:
        csv_file_path = line[line.index('=')+1:]    #Relative Path to the CSV file (results)
        print('File path:', csv_file_path)
    if 'Electronic Load GPIBAddr' in line:
        electronic_load_GPIBAddr = int(line[line.index('=')+1:])    #Electronic load GPIB address
        print('Electronic Load GPIBAddr:', electronic_load_GPIBAddr)
    if 'Keithley 3706 GPIBAddr' in line:
        multimeter_GPIBAddr = int(line[line.index('=')+1:])    #Keithley multimeter GPIB address
        print('Keithley 3706 GPIBAddr:', multimeter_GPIBAddr)
        

initial_values_f.close()    #In order to avoid errors, the file is closed
print('\n---------------------------------------------------------------')




def check_time_parameters(_t_on, _t_off, _t_measure_high, _t_measure_low, _t_transfer_data):    
    '''
    This function checks whether the times are coherent. It returns an error if any of the 
    following sentences happen, as well as a reporting message.
    '''
    error = False    #Initial error status=False
    
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
    if t_on<0 or t_off<0 or t_measure_high<0 or t_measure_low<0 or t_transfer_data<0:    #Negative times 
        error = True
        messagebox.showerror(message="Times must be positive", title="Time Definition Error")
    
    return error


#Check if all the times are OK
if check_time_parameters(t_on, t_off, t_measure_high, t_measure_low, t_transfer_data)==True:
    exit()    #If any mentioned fact has happened, the program exits. 


#Define the total number of channels
nChannels = nTemperatureChannels + nVoltageChannels + nCurrentChannels      

#CREATE AND OPEN THE CSV FILE TO TRANSFR THE ACQUIRED DATA
field_names = ['Number of cycles', 'Semicycle']    #Create an array of constant headers
for channel in range(1, nChannels+1):    #Headers depend on the number of channels
    field_names.append(str(channel))   #Append the channels after the constant headers
        
csv_connection.create_csv_file(csv_file_path, field_names)    #Open the csv file and write the array of headers

#---------------------------------------------------------------------------------------------


#COUNTER OF CYCLES DONE AND A STOP BUTTON
cycle_count = 0   #Initialize the number of cycles 
stop = 0    #Boolean in order to stop the electronic load whenever necessary. 


#DEFINING THE BUFFER CHARACTERISTICS
nScansPerSemicicle = 2    #Number of scans per cycle: -Measure when current is high, -Measure when current is low
#One Scan=Measure of all channels
bufferSize = nScansPerSemicicle*(nChannels)   #Capacity of the buffer will be the number of channels times the number of scans
#The buffer will be emptied each cycle
bufferName = "reading_buffer"

#OPENING THE RESOURCE MANAGER
rm = visa.ResourceManager()


#COMMUTICATE WITH THE ELECTRONIC LOAD 
electronic_load = rm.open_resource('GPIB0::'+str(electronic_load_GPIBAddr)+'::INSTR')   #Assign a variable to the Electronic load by its address

#COMMUTICATE WITH KEITHLEY MULTIMETER
multimeter = rm.open_resource('GPIB0::'+str(multimeter_GPIBAddr)+'::INSTR')   #Assign a variable to the multimeter by its address


#SENDING THE FIRST COMMANDS TO CONFIGURE THE ELECTRONIC LOAD
electronic_load.write('*CLS')    #Clear Status Command
electronic_load.write('*RST')    #Reset Command 
electronic_load.write('TRIG:SOUR BUS')    #Source triggeR will be send via bus
electronic_load.write('MODE:CURR')    #Set the operating mode: Current Mode (CC)
electronic_load.write('CURR:RANG {}'.format(curr_rang))    #Low range current (0A-6A), High range current (0A-60A)
electronic_load.write('CURR:SLEW {}'.format(sr))    #The value of the Slew Rate in the file is imposed on the instrument 
electronic_load.write('CURR {}'.format(curr_low))    #The value of the low current is established on the instrument
electronic_load.write('INPUT ON')    #Switch on electronic load



#SENDING THE FIRST COMMANDS TO CONFIGURE KEITHLEY MULTIMETER
multimeter.write('reset()')    #Reset
multimeter.write('localnode.prompts = 0')    #The command messages do not generate prompts in console
multimeter.write('localnode.prompts4882 = 0')    #Disable the prompts for the GPIB

#Set voltage configuration
multimeter.write('dmm.func = dmm.DC_VOLTS')    #Set measurement function: Voltage
multimeter.write('dmm.nplc=1')    #The integration rate in line cycles for the DMM for the function selected by dmm.func.
multimeter.write('dmm.range=10')    #Set Range
multimeter.write("dmm.configure.set('mydcvolts')")    #Save Configuration
multimeter.write("dmm.setconfig('"+voltageChannelsString+"','mydcvolts')")

#Set current configuration (one voltage channel reserved to measure the current)
multimeter.write("dmm.configure.set('mycurrent')")    #Save Configuration
multimeter.write("dmm.setconfig('"+currentChannelsString+"','mycurrent')")

#Set temperature configuration
multimeter.write('dmm.func = "temperature"')    #Set measurement function: Temperature
multimeter.write('dmm.transducer = dmm.TEMP_THERMOCOUPLE')    #Type of transducer: Thermocouple
multimeter.write('dmm.thermocouple = dmm.THERMOCOUPLE_K')    #Type of thermocouple: K
multimeter.write("dmm.configure.set('mythermocouple')")    #Save Configuration   
multimeter.write("dmm.setconfig('"+temperatureChannelsString+"','mythermocouple')")    #Assign configuration to channels


try:        
    #DEFINING PRINCIPAL FUNCTION
    def make_buffer(_bufferSize):
        '''
        This function creates the buffer with a certain capacity
        '''
        multimeter.write(str(bufferName)+'=dmm.makebuffer('+str(_bufferSize)+')')    #Configure the reading buffer
        multimeter.write(str(bufferName)+'.clear()')      
        
      
    def prepare_Scan(_n_total_channels,_nScansPerSemicicle):
        '''
        This function sets the number of channels and remains quiet till a trigger is sent.
        '''
        #Whether the first channel of the scan waits for the channel stimulus event to be satisfied before closing   
        multimeter.write('scan.bypass=scan.OFF')    
        
        #Creates an scan with a fixed number of voltage channels and adds a scan for the temperature channels
        multimeter.write("scan.create('"+voltageChannelsString+"','mydcvolts')")
        multimeter.write("scan.add('"+temperatureChannelsString+"','mythermocouple')")
        multimeter.write("scan.add('"+currentChannelsString+"','mycurrent')")
        
        
        #Prepares the scan to be waiting for a trigger
        multimeter.write('scan.trigger.arm.stimulus = 40')    #Which event starts the scan, 40 = trigger via GPIB, a *trg message
        multimeter.write("scan.scancount="+str(_nScansPerSemicicle))
        multimeter.write('scan.background('+str(bufferName)+')')
        
      
    def start_scan_multimeter():
        '''
        This function sends the trigger to the Keithley Multimeter in order to make the measures
        in a predetermined time (when current is low or high)
        '''
        
        multimeter.write('*TRG')   #This command sends the trigger to the multimeter in order to make a measure
         
       
        
    def read_multimeter_buffer_and_write_to_file(_csv_file_path, _n_total_channels, _cycle_count): 
        '''
        This function acquire the stored data in the multimeter buffer and write all the information needed to the csv file
        '''
        #ASK for the stored data (and make few superficial changes)
        acq_data = multimeter.query('printbuffer(1,'+str(bufferSize)+','+str(bufferName)+')').replace("\n","").split(",")
        print('Cycle {}:'.format(cycle_count), acq_data)
        
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
        #Configure a timer which calls the function trg_down when the _t_on finishes
        timer_on = threading.Timer(_t_on, trg_down, [_curr_low,_curr_high, _t_on, _t_off, _t_measure_high, _t_measure_low,_t_transfer_data])
        #Configure another timer to claim that the measures will be done at a chosen time: t_measure_high, when the current is high.
        timer_measure_high = threading.Timer(_t_measure_high, start_scan_multimeter)
            
            
        if stop == 0: #Nobody has pressed the stop button 
                    
            make_buffer(bufferSize)  
            prepare_Scan(nChannels,nScansPerSemicicle)
            
                  
            global cycle_count    #As cycle_count is not an argument of the function, the variable must be global
            cycle_count = cycle_count + 1    #It increased at each rising current edge
            
            #Commands  low>high
            electronic_load.write('CURR:TRIG {}'.format(_curr_high))    #Intensity value on memory, Preset
            electronic_load.write('*TRG')    #Send trigger signal
            
            #Start the timers
            timer_on.start()     
            timer_measure_high.start()
            
            
        if stop == 1:    #Someone has pressed the stop button
            
            print("CANCELLING THE PROCESS!!!!!!!")
            print("CANCELLING THE PROCESS!!!!!!!")
            print("CANCELLING THE PROCESS!!!!!!!")
            
            #Timers are closed in order to avoid errors
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
        #Configure a timer that calls the function trg_up (when the _t_off finishes). 
        timer_off = threading.Timer(_t_off, trg_up, [_curr_low,_curr_high, _t_on, _t_off, _t_measure_high, _t_measure_low, _t_transfer_data])
        #The two functions (trg_up and trg_down) will be calling each other for ever and ever, except someone pushes the stop button (=space bar)
        #Another timer to claim that the measures will be done at a chosen time: t_measure_on, when the current is low.
        timer_measure_low = threading.Timer(_t_measure_low, start_scan_multimeter)
        
        #In this case, when the cycle has finished and the current is low, the store data (two scans) in the buffer has to be transfered via GPIB.
        #That is for releasing the buffer capacity  
        timer_transfer = threading.Timer(_t_transfer_data, read_multimeter_buffer_and_write_to_file, [csv_file_path, nChannels, cycle_count])
    
      
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
            
            print('STOP!!!')
            global stop    #Stop is converted to a global variable
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

except visa.VisaIOError as e:
#except SomeException:
    print(e.args)
    print(rm.last_status)
    print(rm.visalib.last_status)
    
    if rm.last_status == visa.constants.StatusCode.error_resource_busy:
        print("The port is busy!")
  
    
    print('holiiiiiiiiiiiiiiiiiiiiii')
    electronic_load.write('INPUT OFF')
    

