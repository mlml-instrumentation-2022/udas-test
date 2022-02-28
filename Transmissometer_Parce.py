import serial
import time
import csv
from datetime import datetime

port = '/dev/ttyUSB0'
baud = 19200

filename = str('transmissometer'+str(datetime.now())+'.csv')
file_init = open(filename,'w')
writer = csv.writer(file_init)
header = ['Datetime', 'Transmission']
writer.writerow(header)
file_init.close()

i=1
for i in range(61):
    with serial.Serial(port,baud,timeout=1) as sensor:
        data = sensor.readline().decode()
        index = data.split()
        timestamp = datetime.now()
        time.sleep(0.70)
    print(timestamp,index[4])
    i = i+1
    f = open(filename,'a')
    writer = csv.writer(f)
    writer.writerow([str(timestamp), str(index[4])])
    f.close()