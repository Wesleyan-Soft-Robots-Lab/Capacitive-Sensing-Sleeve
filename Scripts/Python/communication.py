import os
import serial
import time

class Sensor:
    def __init__(self, id):
        self.id = id
        self.value = 0 # in femtoFarads
        self.lowestValue = 20000 
        self.highestValue = 40000
        #self.timestamp = time.time()

    def __str__(self):
        return f"Sensor(id={self.id}, value={self.value}, lowestValue={self.lowestValue}, highestValue={self.highestValue})"
    
    def Update(self, value):
        self.value = value
        if value < self.lowestValue:
            self.lowestValue = value
        if value > self.highestValue:
            self.highestValue = value

Sleeve = dict[int, Sensor]()

"""
Methods 
"""
def ReadPort():
    line = arduino.readline().decode('utf-8').strip()
    if not line:
        return
    for chunk in line.split(';'):
        if len(chunk) < 2:
            continue
        id,val = chunk.split(",")

        if id not in Sleeve:
            Sleeve[id] = Sensor(id)

        Sleeve[id].Update(int(val))
""" 
Script Start
"""
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

while True:
    ReadPort()
    for patch in Sleeve:
        print(Sleeve[patch])
