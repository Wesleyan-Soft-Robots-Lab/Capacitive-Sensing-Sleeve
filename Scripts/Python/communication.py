""" 
Name: Miles Modeste
Date Created: 6/11/2025
Last Updated: 6/12/2025

Description:
  This script is used to communicate between the Arduino and Python. This module must be imported in xArm behavior scripts. 

TODO:
    - Add speed check
"""
import os
import serial
import time

class Sensor:
    def __init__(self, id):
        self.id = id
        self.value = 0 # in femtoFarads
        self.lowestValue = 18000 
        self.highestValue = 18000
        self.percent = 0
        #self.timestamp = time.time()

    def __str__(self):
        return f"Sensor(id={self.id}, value={self.value}, lowestValue={self.lowestValue}, highestValue={self.highestValue})"
    
    def getPercent(self, v)->float:
        scale = self.highestValue - self.lowestValue
        if (v==0 or scale==0):
            return 0.0
        return (v - self.lowestValue) / scale * 100
    
    def Update(self, value):
        self.value = value
        self.percent = self.getPercent(value)
        if value < self.lowestValue:
            self.lowestValue = value
        if value > self.highestValue:
            self.highestValue = value
"""
Methods 
"""
def ReadPort() -> bool:
    line = arduino.readline().decode('utf-8').strip()
    if not line:
        return False   
    for chunk in line.split(';'):
        if len(chunk) < 2:
            continue
        id,val = chunk.split(",")
        if id not in Sensors:
            Sensors[id] = Sensor(id)
        Sensors[id].Update(int(val))
    return True

def UpdateReadings()-> dict[int, Sensor]:
    ReadPort()
    return Sensors

""" 
MAIN
"""
Sensors = dict[int, Sensor]()
timestamp = time.time()
printDelay = 5  # seconds
while True:
    try:
        arduino = serial.Serial(port='COM10',   baudrate=115200, timeout=.1)
        break
    except serial.SerialException as e:
        if time.time() - timestamp > printDelay:
            timestamp = time.time()
            print(f"Error opening serial port. Check if the Arduino is connected...")

if __name__ == "__main__":
    while True:
        ReadPort()
        for patch in Sensors:
            print(Sensors[patch])