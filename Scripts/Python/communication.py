""" 
Author: Miles Modeste
Co-editor: Yamani Mpofu
Date Created: 6/11/2025
Last Updated: 6/12/2025

Description:
  This script is used to communicate between the Arduino and Python and test the speed of different encoding methods. 

TODO:
    - Saftey feature to not be able to read measurements until sensor hi/lo has been
      calibrated. (Hard Press to calibrate)
    - Add sensor method for calculating percent readings to standardize thresholds
      (total percentage, and percent increase/decrease)

"""

import os
import sys
import time
import math
import serial
from xarm.wrapper import XArmAPI

class Sensor:
    def __init__(self, id):
        self.id = id
        self.value = 0 # in femtoFarads
        self.lowestValue = 500000 
        self.highestValue = 0
        self.threshold = 50000
        #self.timestamp = time.time()

    def __str__(self):
        return f"Sensor(id={self.id}, value={self.value}, lowestValue={self.lowestValue}, highestValue={self.highestValue}, threshold={self.threshold})"
    
    def Update(self, value):
        self.value = value
        if value < self.lowestValue:
            self.lowestValue = value
        if value > self.highestValue:
            self.highestValue = value
            self.threshold = self.lowestValue + ((self.highestValue - self.lowestValue)*0.35)

# Globals
SERIAL_PORT = "/dev/tty.usbmodem101"     # Linux/Mac example
#SERIAL_PORT = "COM10"                       # Windows example
BAUD_RATE = 115200 

"""
Methods 
"""
#safety check before running the script - calibrate sensors

def updatereadings() -> dict[int, Sensor]:
    ReadPort()
    return Sleeve
    
def calibrate_sensors():
    print("Sensors stabilizing...")
    time.sleep(5)  # Allow sensors to settle
    print("Reading initial values...")
    ReadPort()  # Get the initial baseline values

    # Initialize storage dictionaries
    
   # **no need for memory data structure right now since we have few sensors and can calibrate one at a time, keeping this dict for when there are more sensors and we want to calibrate in parallel.**
    id_min_val = {} 
    id_max_val = {}

    for sensor_id, sensor in Sleeve.items():
        id_min_val[sensor_id] = sensor.value  # Baseline value before press

        print(f"\nPlease hard press on sensor {sensor.id} to calibrate.\n")
        user = input("Press 'y' while holding to continue, or 'n' to cancel: ")

        if user.lower() == 'y':
            start_time = time.time()
            while time.time() - start_time < 3:#reading the max press value
                ReadPort()
            sensor = Sleeve[sensor_id] #current sensor object
            id_max_val[sensor_id] = sensor.highestValue # storing the highest values
            diff = id_max_val[sensor.id] - id_min_val[sensor_id]
            print(f"Sensor {sensor.id} value after hard press: {sensor.value}, min: {id_min_val[sensor.id]}, max: {id_max_val[sensor.id]}")
            
            # Calculate threshold as 35 % of the difference
            
            if abs(diff) < (0.2 * id_min_val[sensor_id]): 
                sensor.threshold = id_min_val[sensor_id] + 0.35 * id_min_val[sensor_id]  # Set a minimum threshold to avoid too small values
                print(f"Warning: Sensor {sensor.id} has a very small delta ({diff}). Calibration threshold set to default 35% of initial value.")
            else:
                sensor.threshold = id_min_val[sensor_id] + 0.35 * diff
                
    # Final confirmation
    user = input("\nCalibration complete. After confirmation, please take a few steps back from the arm\nPress 'y' when ready or 'n' to cancel: ")
    while user.lower() not in ['y', 'n']:
        user = input("Invalid input. Type 'y' when ready or 'n' to cancel: ")

    if user.lower() == 'n':
        print("Calibration cancelled.")
        return False

    print("stand clear....")
    time.sleep(5)
    print("Done, arm is ready")
    return True

    
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
            arduino = serial.Serial(port= SERIAL_PORT,   baudrate=115200, timeout=.1)
            break
        except serial.SerialException as e:
            if time.time() - timestamp > printDelay:
                timestamp = time.time()
                print(f"Error opening serial port. Check if the Arduino is connected...")
    
    


main()

if __name__=="__main__":
    #implementing the safety check before running the script
    if calibrate_sensors():
        while True:
            ReadPort()
            for patch in Sleeve:
                print(Sleeve[patch])
    else:
        print("Calibration failed. Exiting...")
