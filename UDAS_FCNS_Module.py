##UDAS Functions File_MS202_Spring_2022
#Contains functions to run the various sensors configured to the UDAS system

import numpy as np
import serial
from datetime import datetime
import time
import csv


# Fucnction to retrieve the TSG sensor Data
# TSG sensor provides data for Temperature (C), conductivity, and salinity (PSU)
def getTSG(TSG_sensor):
    '''Obtain temperature, conducivity, and practical salinity measurments from TSG sensor.
        
        INPUTS:
           TSG_sensor - a serial object
        
        RETURNS:
        temperature (Celsius)
        conductivity
        salinity
        '''
    try:
        data = TSG_sensor.readline().decode()
        split = data.split(',')
        data_T = float(split[0])
        data_C = float(split[1])
        data_S = float(split[2])
        
        return(data_T,data_C,data_S)
            
    except:
        print('No data collected')
        data_T = 'nan'
        data_C = 'nan'
        data_S = 'nan'
        return (data_T, data_C, data_S)


#=========================================================
# Function to Retrive SUNA sensor data
# SUNA sensor provides nitrate data (NO3)
def getSUNA(suna,nsample):
    '''
    Obtain nitrate measurement from SUNA sensor operating in polled mode.
    
    This version has been tested on Python 3 only.
    
    INPUTS:
    suna - a Serial object
    nsample - number of light samples to average
    
    RETURNS
    nitrate_uM (umol/L)
    nitrogen (mg/L)
    '''
    
    try:
        print('Connected to SUNA'+'\n')
        
        suna.write(b'Waking up SUNA\n')
        wake1 = suna.readline().decode()
        #print('wake1: ' + wake1+'\n')
        wake2 = suna.readline().decode()
        #print('wake2: ' + wake2+'\n')
        #print('Woken up SUNA, exit from command line'+'\n')
        suna.write(b'exit\n')
        
        #wait a few secs
        time.sleep(10)
        
        #SATSDF: SUNA Dark Full: blank dark reading
        #SATSLF: this has the data in it. Check SUNA hardware manual pg 58 for column headers
        #... full ascii column
        
        #Request data, take samples and average them together
        sample_command = 'measure '+str(nsample)+'\n'
        try:
            suna.write(sample_command)
        except:
            suna.write(str.encode(sample_command))
            
        nitrate_list=[]
        nitrogen_list = []
                
        count = 1
        # Loop through until done, limit to nsample*10 to avoid infinite loop
        for i in range(nsample*2):
            try:
                line=suna.readline().decode()
            except:
                line=suna.readline()
            #print('Line: '+line+'\n')
            if 'SATSL' in line:
                #Only average the light counts
                data = line.split(',')
                nitrate_list.append(float(data[3]))
                nitrogen_list.append(float(data[4]))
                count = count+1
            if count > nsample:
                break
        
        suna.close()
        
        
        
        data = line.split(',')
        nitrate_uM = np.mean(nitrate_list)
        nitrogen = np.mean(nitrogen_list)
        
        
        print ('*****************************************\n')
        print ('Nitrate (uM): '+str(nitrate_uM)+'\n')
        print ('Nitrogen (mg/L): '+str(nitrogen)+'\n')
        print ('*****************************************\n')
        
        
        return (nitrate_uM, nitrogen)

    
    except:
        
        print ('No data received from SUNA.'+'\n')
        return ('NA','NA')

#==================================================================================
# Function to retrieve data from the transmissometer sensor
# Transmissometer sensor provides data for beam attenuation
def get_Transmissometer(TM_Sensor):
    '''Obtain transmisometer data from transmissometer sensor.

        Inputs:
            TMSensor - a serial object
        
        Outputs:
            Beam_Attenuation
        '''
    try:
        data = TM_Sensor.readline().decode()
        index = data.split()
        Beam_Attenuation = float(index[4])
        return Beam_Attenuation
    
    except:
        print('No data collected')
        Beam_Attenuation = 'nan'
        return Beam_Attenuation
    
#===============================================================
#Chlorophyll 
def get_chla(chla_sensor):
    ''' Obtain Chlorophyl a and turbidity measurments.
        
        INPUTS:
           chla_sensor - a serial object
        
        RETURNS:
        Chl_a (chlorophyll a)
        turb (Turbidity)

    '''
    try:
        data = chla_sensor.readline().decode()
        split = data.split()
        chl_a = float(split[3])
        turb = float(split[4])
        return chl_a,turb
    
    except:
        print('No data collected')
        chl_a = 'nan'
        turb = 'nan'
        return chl_a,turb
