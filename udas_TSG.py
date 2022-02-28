from datetime import datetime
import time as t
import csv
import serial

port = '/dev/ttyUSB0'
baud = 38400 #bits per second (rate of information/second)
time = datetime.now()
sensor = serial.Serial(port, baud, timeout=1) #waits 1 second between measurements



f = open('TSG_UDAS.csv','w')
header = csv.writer(f)
header.writerow(['Time (PST)','TempC','Conductivity', 'Salinity'])
f.close()

while True:
    f = open('TSG_UDAS.csv','a')
    
    with serial.Serial(port, baud, timeout=1) as sensor:
        data = sensor.readline().decode()
        split = data.split(',')
        #data_T = split[0].replace(',','')
        #data_C = split[1].replace(',','')
        #data_S = split[2].replace(',','')
        
        #print(time, data_T,data_C,data_S)

    writer = csv.writer(f)
    writer.writerow([str(time),float(split[0]),float(split[1]),float(split[2])])
    
    t.sleep(1)
    time = datetime.now()
    
    f.close()

