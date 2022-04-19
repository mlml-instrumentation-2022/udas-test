#UDAS Master Compilation Code (MLML_MS_202_Spring_2022)
#Contatins code to run the sensors attached to the UDAS using funcitons stored in UDAS_FCNS_Module.py

import numpy as np
import serial
from datetime import datetime
import time
import csv
import UDAS_FCNS_Module as udas
import board
import busio
import adafruit_gps
import io
import pynmea2

#===================================================================================
#Enter the correct ports for each sensor pluged into the Raspberry Pi USB ports
#To identify the correct port plug in one sensor at a time. After the sensor is plugged in
#go to the terminal and type the command "ls /dev/ttyUSB*" (without the quotes). The readout will tell you
#which USB port that sensor is using (e.g. /dev/ttyUSB0, /dev/ttyUSB1...). Modfy the code below for each sensor.

TSG_port = '/dev/ttyUSB2' #USB port the Temperature Salinograph is plugged into

COM_SUNA = '/dev/ttyUSB3' #USB port the SUNA Nitrate sensor is pluged into

TM_port  = '/dev/ttyUSB0' #USB port the Transmissimeter is plugged into

chl_port = '/dev/ttyUSB1' #USB port the Fluormeter is plugged into

gps_port = '/dev/ttyS0'   #Plugged into serial port using wires. SHOULD NOT NEED TO BE CHANGED 
#===================================================================================

# Create CSV File with proper headers to store the data collected from the sensors
file_time = datetime.now() #local time at which the porgram is started for data collection
file_name = 'UDAS/UDAS_'+str(file_time)+'.csv' #file the data is stored if which can be found in the "UDAS" folder
f = open(file_name,'w')

#Define the headers
header = csv.writer(f) 
header.writerow(['Time (UTC)','Local_Time (PDT)','Latitude','Longitude','TempC','Conductivity', 'Salinity','Nitrate (uM)','Nitrogen (mg/L)','Chl_a','Turbidity','Transmission'])
f.close()

#=================================================================================
#Seperate GPS variables defined
ser = serial.Serial(gps_port, baudrate=9600, timeout=1)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

# Create a GPS module instance
gps = adafruit_gps.GPS(ser)

# Turn on the basic GGA (the 4th digit after 'PMTK314' is a 1, denoting that GGA is 'on'. The 2nd digit would enable RMC if desired.)
gps.send_command(b"PMTK314,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command(b"PMTK220,1000")
#===================================================================================

while True:
#Read out the data from all the sensors then record it in a csv file (UDAS+start time) in the folder "UDAS"  
    #Get data from TSG (Temp, conductivity, Salinity)
    Temp,Conductivity,Salinity = udas.getTSG(TSG_port)
    
    #Get Data from the SUNA Sensor (Nitrate)
    nsample = 5        # number of light frames averaged together - should be greater than 4 (SUNA).
    nitrate_uM,nitrogen = udas.getSUNA(COM_SUNA,nsample)
    SUNA_sensor.close()
    
    #Get data from Transmissimeter (Beam attenuation)
    Beam_Attenuation = udas.get_Transmissometer(TM_port)
    
    #Get Data from Fluorometer (Cholarphyl A and turbidity)
    chl_a,turb = udas.get_chla(chla_port)
    
    #Get gps coordinates from gps
    lat,lon = udas.get_gps(sio)
#--------------------------------------------------------------------------------------    
    #Add data to CSV file
    f = open(file_name,'a')
    writer = csv.writer(f)
    time_now = datetime.now()
    time_UTC = datetime.utcnow()
    writer.writerow([str(time_UTC), str(time_now),lat, lon, Temp, Conductivity, Salinity, nitrate_uM, nitrogen, chl_a, turb, Beam_Attenuation])
    time.sleep(3)  
    f.close()
#--------------------------------------------------------------------------------------
    
    #Print everything - used to test the code and make sure all are reading out
    print(str(time_now),str(lat), str(lon), str(Temp), str(Conductivity), str(Salinity),
          str(nitrate_uM), str(nitrogen), str(chl_a), str(turb), str(Beam_Attenuation))
    print('---------------------------------------------------------------------------------------')
    print()