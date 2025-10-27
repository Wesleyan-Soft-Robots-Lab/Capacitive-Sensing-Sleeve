""" 
Name: Miles Modeste
Date Created: 6/11/2025
Last Updated: 8/5/2025

Description:
  This script is used to communicate between the Arduino and Python. This module must be imported in xArm behavior scripts (gui handels import too). 

"""
import serial
import time
import data_logger as logger

COM = "/dev/cu.usbmodem1101" 
FDC_SCALAR = 0x80000
CAPDAC_SCALAR = 3.125 # what is this scalar?

class Sensor:
    def __init__(self, id):
        self.id = id                # id int8 representation of [mux, port, channel]:(3,3,2 bits) (Max Individual Sensor "square pixel": 256)
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

    def getPercent(self, v:float)->float:
        scale = self.hiVal - self.loVal
        if (v==0 or scale==0):
            return 0.0
        percent = (v - self.loVal) / scale * 100
        return round(percent, 2)
    
    def Calibrate(self):
        """ 
        Takes a window average of the lo point, then window average of hi point,
        creating our scale for percentage readings.  
        """
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
        """
            Updates the value reading and adjusts the percentage accordingly
        """
        self.value = value
        self.percent = self.getPercent(value)   

"""
Methods 
""" 
def ConvertToPF(raw_value:int, capdac:int) -> float:
    """ 
    Converts raw measurement to picofarads using equation:
        Capacitance (pf) = (measurement [23:0]) / 2^19 ) + C_offset
    """
    C_offset = float(capdac) * float(CAPDAC_SCALAR)
    capacitance_pF = (float(raw_value) / float(FDC_SCALAR)) + C_offset
    return capacitance_pF

def OpenConnection(port=COM, baudrate=115200, timeout=.1)-> serial.Serial:
    """ Open serial connection to arduino. Retries until successful."""

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
    """ Converts an unsigned value to signed value based on bit length. """
    if value >= 2**(bits - 1):
        return value - 2**bits
    else:
        return value
         
def ReadPort() -> dict[int, Sensor]:
    """ 
    Reads from arduino and updates Sensor vals.
    
    Returns: updated dict of Sensors

    Format in bytes:
        0xAA 1b |      n 1b    |       id 1b     | Sensor Val 3b  | *n 
        header  | sensor_count | mux | port | ch | value | capdac | ...
    """
    try:
        header = arduino.read(size=1)
        if header == b'':
            return Sensors
        elif header == b'\xAA':
            payload_size = int.from_bytes(arduino.read(size=1), 'big')
            for i in range(payload_size):
                data = arduino.read(size=5)
                if len(data) < 5:
                    raise ValueError("Incomplete data received.")
                id = data[0]
                raw_val = toSigned((data[1] << 16) | (data[2] << 8) | data[3], 24)
                
                capdac = data[4] & 0b1111
                if capdac == 30:
                    print(f"Sensor {id} capdac is 31...")
                val = ConvertToPF(raw_val, capdac)
                
                # create a new Sensor if the id doesn't exist in the dictionary
                if id not in Sensors:
                    Sensors[id] = Sensor(id)
                # update the sensor in the dictionary
                Sensors[id].Update(val)

        """ might be useful to add algorithm to match the receive speed to the arduino's transmit speed
        this delay is proportional to the number of sensors connected. not sure by how much
        e.g. if only 4 patches no delay needed.  """
        #time.sleep(.1) 
        return Sensors
    except ValueError as ve:
        #print(f"ValueError: {ve}")
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

startTime = logger.startTimer()

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
        # Create a single row list for all sensors in this timestamp
        current_time = time.time()
        elapsedTime = logger.elapsedTimeMilliseconds(startTime, current_time)
        rows = []
        
        for i,s in Sensors.items():
            if not s.isCalibrated:
                s.Calibrate()
                pass
            # Add data for each sensor
            rows.append([elapsedTime, i, f"{s.value:0.2f}"])
            msg += f"{i}: {s.value:0.2f}pF  \n"
            
        if msg:
            print(msg)
        # Only log if we have sensor data
        if rows:
            logger.logData(rows)