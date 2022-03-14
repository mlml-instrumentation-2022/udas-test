from datetime import datetime
import time as t
import csv
import serial


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
        data = TSGsensor.readline().decode()
        split = data.split(',')
        Temp = split[0].replace(',','')
        Conductivity = split[1].replace(',','')
        Salinity = split[2].replace(',','')
        
        print(Temp,Conductivity,Salinity)
        return Temp,Conductivity,Salinity
            
    except:
        print('No data collected')
        Temp = 'nan'
        Conductivity = 'nan'
        Salinity = 'nan'
        return Temp,Conductivity,Salinity
        

f = open('TSG_UDAS.csv','w')
header = csv.writer(f)
header.writerow(['Time (PST)','TempC','Conductivity', 'Salinity'])
f.close()

while True:
    TSG_port = '/dev/ttyUSB0'
    TSGsensor = serial.Serial(TSG_port, 38400, timeout=1) #waits 1 second between measurements. Specifies USB port and baud rate. 
    Temp,Conductivity,Salinity = getTSG(TSGsensor)
    time = datetime.now()
    
    f = open('TSG_UDAS.csv','a')
    writer = csv.writer(f)
    writer.writerow([str(time),Temp,Conductivity,Salinity])
    t.sleep(3)
    f.close()
