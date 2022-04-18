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
# Create CSV File with proper headers
file_time = datetime.now()
file_name = 'UDAS/UDAS_'+str(file_time)+'.csv'
f = open(file_name,'w')
header = csv.writer(f)
header.writerow(['Time (UTC)','Time (PST)','Latitude','Longitude','TempC','Conductivity', 'Salinity','Nitrate (uM)','Nitrogen (mg/L)','Chl_a','Turbidity','Transmission'])
f.close()

#=================================================================================
#Seperate GPS variables defined
gps_port = '/dev/ttyS0'
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
    #Get data from TSG (Temp, conductivity, Salinity)
    TSG_port = '/dev/ttyUSB2'
    TSGsensor = serial.Serial(TSG_port, 38400, timeout=5) #waits 1 second between measurements. Specifies USB port and baud rate. 
    Temp,Conductivity,Salinity = udas.getTSG(TSGsensor)
    print(Temp, Conductivity, Salinity)
    

    #Get Data from the SUNA Sensor (Nitrate)
    COM_SUNA = '/dev/ttyUSB3'  # COM port for the SUNA
    nsample = 5       # number of light frames averaged together - should be greater than 4 (SUNA).
    SUNA_sensor = serial.Serial(COM_SUNA,57600,timeout=10)
    nitrate_uM,nitrogen = udas.getSUNA(SUNA_sensor,nsample)
    SUNA_sensor.close()
    
    #Get data from Transmissimeter
    TM_port = '/dev/ttyUSB0'
    TMsensor = serial.Serial(TM_port, 19200, timeout=1) #waits 1 second between measurements. Specifies USB port and baud rate. 
    Beam_Attenuation = udas.get_Transmissometer(TMsensor)
    
    #Get Data from Chlorometer
    chl_port = '/dev/ttyUSB1'
    chla_sensor = serial.Serial(chl_port, 9600, timeout=1, rtscts=1)
    chl_a,turb = udas.get_chla(chla_sensor)
    #print(chl_a,turb)
    
    #Get gps coordinates from gps
    lat,lon = udas.get_gps(sio)
    
    
    ##Adds data to CSV file
    f = open(file_name,'a')
    writer = csv.writer(f)
    time_now = datetime.now()
    time_UTC = datetime.utcnow()
    writer.writerow([str(time_UTC), str(time_now),lat, lon, Temp,Conductivity, Salinity,nitrate_uM,nitrogen, chl_a, turb, Beam_Attenuation])
    time.sleep(3)  
    f.close()
    
    #Print everything
    print(str(time_now),str(lat), str(lon), str(Temp), str(Conductivity), str(Salinity),
          str(nitrate_uM), str(nitrogen), str(chl_a), str(turb), str(Beam_Attenuation))
    print('------------------------------------------')
    print()