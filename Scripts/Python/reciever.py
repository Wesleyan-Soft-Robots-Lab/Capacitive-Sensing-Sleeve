""" 
Name: Miles Modeste
Date Created: 6/11/2025
Last Updated: 6/30/2025

Description:
  This script is used to communicate between the Arduino and Python. This module must be imported in xArm behavior scripts (gui handels import too). 

"""
import serial
import time

FDC_SCALAR = 0x80000
CAPDAC_SCALAR = 3.125

class Sensor:
    def __init__(self, id):
        self.id = id                # id int8 representation of [mux, port, channel]:(3,3,2 bits)
        self.addr= id>>5
        self.port= id>>2 & 0b111
        self.channel = id & 0b11
        self.value = 0              # in pF
        self.loVal = 4.2 
        self.hiVal = 40
        self.percent = 0
        self.isCalibrated = False

    def __str__(self):
        return f"Sensor(id={self.id}, value={self.value}, loVal={self.loVal}, hiVal={self.hiVal}, percent={self.percent}, isCalibrated={self.isCalibrated})"
    
    def ConvertToPF(raw_value, capdac) -> float:
        #Convert from raw measurement to picofarads
        #Capacitance (pf) = (measurement [23:0]) / 2^19 ) + C_offset
        C_offset = float(capdac) * float(CAPDAC_SCALAR)
        capacitance_pF = (float(raw_value) / float(FDC_SCALAR)) + C_offset
        return capacitance_pF

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

def toSigned(value, bits):
    if value >= 2**(bits - 1):
        return value - 2**bits
    else:
        return value
         
def ReadPort() -> dict[int, Sensor]:
    """
    Reads from arduino and updates Sensor vals.

    Returns: updated dict of Sensors

    Format in bytes:
        0xAA 1b |      n 1b    {       id 1b     | Sensor data 2b } *n| tail 1b  
        header  | sensor_count { mux | port | ch | value | capdac }...| tail
    """
    try:
        header = arduino.read(1)
        if header == b'':
            print("No data received.")
            return Sensors
        elif header == b'\xAA':
            payload_size = int.from_bytes(arduino.read(1), 'big')
            for i in range(payload_size):
                data = arduino.read(3)
                if len(data) != 3:
                    print("Incomplete data received for sensor.")
                    raise ValueError("Incomplete data")
                id = data[0]
                val = (data[1]<<8 | data[2])/1000

                #capdac = data[3] & 0b1111

                if i not in Sensors:
                    Sensors[i] = Sensor(id)
                Sensors[i].Update(val)

        return Sensors
    except ValueError as ve:
        print(f"ValueError: {ve}")
        return Sensors
    except serial.SerialException as se:
        print(se)
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
        for i,s in Sensors.items():
            if not s.isCalibrated:
                #s.Calibrate()
                pass
            msg += f"{i}: {s.value:.2f}pF({s.percent}%) "
        if msg:
            print(msg)