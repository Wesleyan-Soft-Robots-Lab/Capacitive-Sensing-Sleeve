""" 
Name: Miles Modeste
Date Created: 6/11/2025
Last Updated: 6/12/2025

Description:
  This script is used to communicate between the Arduino and Python and test the speed of different encoding methods. 

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
        self.lowestValue = 20000 
        self.highestValue = 50000
        #self.timestamp = time.time()

    def __str__(self):
        return f"Sensor(id={self.id}, value={self.value}, lowestValue={self.lowestValue}, highestValue={self.highestValue})"
    
    def Update(self, value):
        self.value = value
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

        if id not in Sleeve:
            Sleeve[id] = Sensor(id)

        Sleeve[id].Update(int(val))

    return True

def main():
    global arduino, Sleeve

    Sleeve = dict[int, Sensor]()

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


if __name__ == "__main__":
    main()