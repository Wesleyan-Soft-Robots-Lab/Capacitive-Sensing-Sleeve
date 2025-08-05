""" 
Name: Miles Modeste
Date Created: 6/11/2025
Last Updated: 6/30/2025

Description:
  This script is used to communicate between the Arduino and Python. This module must be imported in xArm behavior scripts. 

"""
import serial
import time

class Sensor:
    def __init__(self, id):
        self.id = id
        self.value = 0 # in femtoFarads
        self.loVal = 4400 
        self.hiVal = 48000
        self.percent = 0
        self.isCalibrated = False

    def __str__(self):
        return f"Sensor(id={self.id}, value={self.value}, loVal={self.loVal}, hiVal={self.hiVal}, percent={self.percent}, isCalibrated={self.isCalibrated})"
    
    def getPercent(self)->float:
        v = self.value
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
        windowSize = 4 # num of intervals
        window = []
        sum = 0

        print(f"Setting Low point. Don't touch for {(windowSize-len(window))*interval:.1f} seconds...")
        clock = time.time()
        while (self.isCalibrated == False):
            # wait for interval b4 update
            # TODO: replace ReadPort() with single sensor read 
            ReadPort()
            delta = time.time() - clock
            if (delta >= interval):
                # set Lo
                if not loPointSet:
                    print(f"{(windowSize-len(window))*interval:.1f} seconds...")
                    window.append(self.value)
                    sum += self.value
                    clock = time.time()
                    if len(window) > windowSize:
                        sum -= window.pop(0)
                        self.loVal = sum / len(window)
                        loPointSet = True

                        self.hiVal = self.loVal + 1000 # set hiVal to be 1000 above loVal
                        window = []
                        sum = 0
                        print(f"Setting Hi point. Hard press {self.id} for {(windowSize-len(window))*interval:.1f} seconds...")
                # set Hi
                else:
                    if self.value >= self.loVal+(self.loVal*hpThres/100):
                        print(f"{(windowSize-len(window))*interval:.1f} seconds...")
                        window.append(self.value)
                        sum += self.value
                        clock = time.time()
                        if len(window) > windowSize:
                            self.isCalibrated = True
                        self.hiVal = sum / len(window)
                    else:
                        print(f"Hard-press {self.id}...")
                        clock = time.time()
                        continue
        return
    
    def Update(self, value):
        """ if not self.isCalibrated:
            print(f"{self.id} is not calibrated yet.") """
        self.value = value
        self.percent = self.getPercent()
        #self.delta = self.getDelta()
        

"""
Methods 
"""
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
        0xAA 1b |      n 1b    {       id 1b     | Sensor data 2b } *n| tail 1b  
        header  | sensor_count { mux | port | ch | int | fraction }...| tail
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