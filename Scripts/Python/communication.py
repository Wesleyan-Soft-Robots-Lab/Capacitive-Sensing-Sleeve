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
        self.value = None # in femtoFarads
        self.loVal = 11000 
        self.hiVal = 30000
        self.percent = 0
        self.isCalibrated = False
        #self.timestamp = time.time()

    def __str__(self):
        return f"Sensor(id={self.id}, value={self.value}, loVal={self.loVal}, hiVal={self.hiVal}, percent={self.percent}, isCalibrated={self.isCalibrated})"
    
    def getPercent(self, v)->float:
        scale = self.hiVal - self.loVal
        if (v==0 or scale==0):
            return 0.0
        percent = (v - self.loVal) / scale * 100
        return round(percent, 2)
    
    def Calibrate(self):
        self.isCalibrated = False
        print(f"Calibrating {self.id}")

        self.loVal = self.value
        
        loPointSet = False
        hpThres = 30 # universal hardpress threshold (%) 

        interval = .5 # in seconds
        windowSize = 10 # num of intervals
        window = []
        sum = 0

        print(f"Setting Low point. Don't touch for {(windowSize-len(window))*interval} seconds...")
        clock = int(time.time())
        while (self.isCalibrated == False):
            # wait for interval b4 update
            # TODO: replace ReadPort() with single sensor read 
            ReadPort()
            delta = int(time.time()) - clock
            if (delta >= interval):
                # set Lo
                if not loPointSet:
                    if self.value >= self.loVal+(self.loVal*hpThres/100):
                        #break from setting lo point if sensor is hard-pressed
                        loPointSet = True

                        self.hiVal = self.loVal + 1000 # set hiVal to be 1000 above loVal
                        window = []
                        sum = 0
                        print(f"Setting Hi point. Hard press {self.id} for {(windowSize-len(window))*interval} seconds...")
                    else:
                        print(f"{(windowSize-len(window))*interval} seconds...")
                        window.append(self.value)
                        sum += self.value
                        clock = int(time.time())
                        if len(window) > windowSize:
                            sum -= window.pop(0)
                        self.loVal = sum / len(window)
                # set Hi
                else:
                    if self.value >= self.loVal+(self.loVal*hpThres/100):
                        print(f"{(windowSize-len(window))*interval} seconds...")
                        window.append(self.value)
                        sum += self.value
                        clock = int(time.time())
                        if len(window) >= windowSize:
                            # break
                            self.isCalibrated = True
                        self.hiVal = sum / len(window)
                    else:
                        print(f"Hard-press on {self.id} NOT detected...")
                        clock = int(time.time())
                        continue
        return
    
    def Update(self, value):
        """ if not self.isCalibrated:
            print(f"{self.id} is not calibrated yet.") """
        self.value = value
        self.percent = self.getPercent(value)
"""
Methods 
"""
def ReadPort()-> dict[int, Sensor]:
    #reads from arduino and updates Sensor vals.
    # TODO: might be more efficient to request only the sensors needed ie for calibration
    line = arduino.readline().decode('utf-8').strip()
    if not line:
        return None
    for chunk in line.split(';'):
        if len(chunk) < 2:
            continue
        try:
            id,val = chunk.split(",")
            if id not in Sensors:
                Sensors[id] = Sensor(id)
            Sensors[id].Update(int(val))  
        except:
            continue
    return Sensors

""" 
MAIN
"""
def Start():
    global Sensors, arduino

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

Start()

if __name__ == "__main__":
    while True:
        ReadPort()
        for patch in Sensors:
            if not Sensors["sensor_0"].isCalibrated:
                Sensors["sensor_0"].Calibrate()
                pass
            print(Sensors["sensor_0"])