# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple GPS module demonstration.
# Will print NMEA sentences received from the GPS, great for testing connection
# Uses the GPS to send some commands, then reads directly from the GPS
import time
import board
import busio
import adafruit_gps
import io
import pynmea2
import serial
import csv
from datetime import datetime

# Create a serial connection for the GPS connection using default speed and
# a slightly higher timeout (GPS modules typically update once a second).
# These are the defaults you should use for the GPS FeatherWing.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
#uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)

# for a computer, use the pyserial library for uart access
ser = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

filename = str('gps'+str(datetime.now())+'.csv')
file_init = open(filename,'w')
writer = csv.writer(file_init)
header = ['Datetime (GMT)', 'Latitude', 'Longitude']
writer.writerow(header)
file_init.close()

# If using I2C, we'll create an I2C interface to talk to using default pins
# i2c = board.I2C()

# Create a GPS module instance.
gps = adafruit_gps.GPS(ser)  # Use UART/pyserial
# gps = adafruit_gps.GPS_GtopI2C(i2c)  # Use I2C interface

# Initialize the GPS module by changing what data it sends and at what rate.
# These are NMEA extensions for PMTK_314_SET_NMEA_OUTPUT and
# PMTK_220_SET_NMEA_UPDATERATE but you can send anything from here to adjust
# the GPS module behavior:
#   https://cdn-shop.adafruit.com/datasheets/PMTK_A11.pdf

# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
# Turn on just minimum info (RMC only, location):
# gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn off everything:
# gps.send_command(b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Tuen on everything (not all of it is parsed!)
# gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command(b"PMTK220,1000")
# Or decrease to once every two seconds by doubling the millisecond value.
# Be sure to also increase your UART timeout above!
# gps.send_command(b'PMTK220,2000')
# You can also speed up the rate, but don't go too fast or else you can lose
# data during parsing.  This would be twice a second (2hz, 500ms delay):
# gps.send_command(b'PMTK220,500')

# Main loop runs forever printing data as it comes in
timestamp = time.monotonic()
while True:
    try:
    #data = gps.read(32)  # read up to 32 bytes
    # print(data)  # this is a bytearray type
        line = sio.readline()
        if line.startswith('$GPGGA'):
            msg= pynmea2.parse(line)
            print(repr(msg.timestamp), repr(msg.lat), repr(msg.lon))
            f = open(filename,'a')
            writer = csv.writer(f)
            writer.writerow([repr(msg.timestamp), repr(msg.lat), repr(msg.lon)])
            f.close()
    except serial.SerialException as e:
        print('Device error: {}'.format(e))
        break
    except pynmea2.ParseError as e:
        print('Parse error: {}'.format(e))
    except AttributeError as e:
        print('Attribute error: {}'.format(e))
        continue

    #if line is not None:
        # convert bytearray to string
        #all "line" variables were previously called "data"
        #data_string = "".join([chr(b) for b in line])
        #print(data_string, end="")

    #if time.monotonic() - timestamp > 5:
        # every 5 seconds...
        #gps.send_command(b"PMTK605")  # request firmware version
        #timestamp = time.monotonic()


