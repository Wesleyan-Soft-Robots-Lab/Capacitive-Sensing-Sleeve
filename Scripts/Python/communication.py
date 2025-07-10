""" 
Author: Miles Modeste
Co-editor: Yamani Mpofu
Date Created: 6/11/2025
Last Updated: 6/30/2025

Description:
  This script is used to communicate between the Arduino and Python. This module must be imported in xArm behavior scripts. 

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
        self.percent = 0
        #self.timestamp = time.time()

    def __str__(self):
        return f"Sensor(id={self.id}, value={self.value}, lowestValue={self.lowestValue}, highestValue={self.highestValue}, percent={self.percent}%)"
    
    def getPercent(self)->float:
        v = self.value
        scale = self.highestValue - self.lowestValue
        if (v==0 or scale==0):
            return 0.0
        percent = (v - self.lowestValue) / scale * 100
        return round(percent, 2)

    
    def Update(self, value):
        """ if not self.isCalibrated:
            print(f"{self.id} is not calibrated yet.") """
        self.value = value
        diff = self.highestValue - self.lowestValue
        if value < self.lowestValue:
            self.lowestValue = value
        if value > self.highestValue:
            self.highestValue = value
        if diff != 0 :
            self.percent = ((self.value - self.lowestValue) / diff)*100

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
            
            # Calculate max_value as 300% increase if poor calibration
            
            if abs(diff) < (0.2 * id_min_val[sensor_id]): 
                sensor.highestValue = 3 * sensor.lowestValue  # Set a minimum threshold to avoid too small values
                print(f"Warning: Sensor {sensor.id} has a very small delta ({diff}). Calibration max set to default 300% of initial value.")
                
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

    
def OpenConnection(port='COM10', baudrate=115200, timeout=.1)-> serial.Serial:
    """
    Open serial connection to arduino. Retries until successful.
    """
    timestamp = time.time()
    printDelay = 5  # seconds
    while True:
        try:
            return serial.Serial(port=port,   baudrate=baudrate, timeout=timeout)
        except serial.SerialException as e:
            if time.time() - timestamp > printDelay:
                timestamp = time.time()
                print(f"Error opening serial port. Check connection...")
            
def ReadPort() -> dict[int, Sensor]:
    """
    Reads from arduino and updates Sensor vals.

    Returns: updated dict of Sensors

    Format in bytes:

        0xAA 1b|      n    1b |      Sensor Data    3b | *n  | "/n" 1b
        header | sensor_count | id | val_msb | val_lsb | ... | tail 
    """
    try:
        time.sleep(.02)
        header = arduino.read(1)
        if header == b'':
            print("No data received.")
            raise
        elif header == b'\xAA':
            payload_size = int.from_bytes(arduino.read(1), 'big')
            for i in range(payload_size):
                data = arduino.read(3)
                id = data[0]
                val = (data[1] << 8) | data[2]
                if id not in Sensors:
                    Sensors[id] = Sensor(id)
                Sensors[id].Update(val)

            tail = arduino.read(1) # bug!! tail not being read correctly
            #print(f"Tail: {tail}") 
        return Sensors
    except:
        print("Error reading from serial port.")
        return Sensors

"""
MAIN
"""

def Start():
    global Sensors, arduino

    Sensors = dict[int, Sensor]()

    arduino = OpenConnection()
    print("Serial port opened successfully.")      

Start()

if __name__ == "__main__":
    while True:
        try:
            Sensors = ReadPort()
        except serial.SerialException:
            print("Serial port disconnected. Check connection...")
            arduino.close()
            time.sleep(1)
            arduino = OpenConnection()
            continue
        
        msg = ""
        for s in Sensors.values():
            if not s.isCalibrated:
                s.Calibrate()
            msg += f"{s.id}: {s.value}fF ({s.percent}%)\t"
        print(msg)