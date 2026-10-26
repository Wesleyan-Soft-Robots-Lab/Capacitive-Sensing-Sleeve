""" 
Name: Miles Modeste
Date Created: 6/11/2025
Last Updated: 8/5/2025

Description:
  This script is used to communicate between the Arduino and Python. This module must be imported in xArm behavior scripts (gui handels import too). 

"""
import serial
import serial.tools.list_ports
import time
import data_logger as logger
import json
import os

def find_arduino_port():
    """
    Automatically chooses the right USB port for arduino communication. 
    """
    ports = serial.tools.list_ports.comports()
    COM = 'NONE'

    numConnect = len(ports)

    for p in ports:
        strPort = str(p)

        if 'IOUSBHostDevice' in strPort:
            splitPort = strPort.split(' ')
            COM = splitPort[0]
    return COM

COM = find_arduino_port()
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
        self.touchVal 
        self.hiVal = 25
        self.Force = 2
        self.butterParam = 2 
        self.averageParam = 2 
        

        self.percent = 0 #
        self.isCalibrated = False

    def __str__(self):
        return f"Sensor(id={self.id}, value={self.value}, loVal={self.loVal}, hiVal={self.hiVal}, percent={self.percent}, isCalibrated={self.isCalibrated})"

    def getPercent(self, v:float)->float:   
        scale = self.hiVal - self.loVal
        if (v==0 or scale==0):
            return 0.0
        percent = (v - self.loVal) / scale * 100
        return round(percent, 2)
    
    def CalibrateFast(self):
        """ 
        Takes a window average of the lo point, then window average of hi point,
        creating our scale for percentage readings.  
        """
        self.isCalibrated = False
        print(f"Calibrating {self.id}")
        if not all(hasattr(self, attr) for attr in
               ("manualLoVal", "manualTouchVal", "manualHiVal")):
            print("Manual calibration required first.")
            return

        touchThreshold = (self.manualLoVal + self.manualTouchVal) / 2
        forceThreshold = (self.manualTouchVal + self.manualHiVal) / 2. #30?
        loPointSet = False
        # hpThres = 30 # universal hardpress threshold (%) 
        interval = 0.25
        windowSize = 8

        phases = ["Near Field", "Touch", "Force"]

        for phase in phases:

            window = []
            total = 0

            # Near Field starts automatically
            if phase == "Near Field":
                print(
                    f"Setting Low point. Don't touch for "
                    f"{windowSize * interval:.1f} seconds..."
                )

            # Touch and Force require automatic detection
            else:
                print(f"Waiting for {phase}...")

                while True:
                    ReadPort()

                    if phase == "Touch" and (
                        touchThreshold <= self.value < forceThreshold
                    ):
                        break

                    elif phase == "Force" and self.value >= forceThreshold:
                        break

                print(
                    f"Setting {phase} point for "
                    f"{windowSize * interval:.1f} seconds..."
                )

            # Begin recording the detected phase
            clock = time.time()

            while len(window) < windowSize:

                ReadPort()
                delta = time.time() - clock

                if delta >= interval:
                    window.append(self.value)
                    total += self.value
                    clock = time.time()

                    print(
                        f"{(windowSize - len(window)) * interval:.1f} seconds..."
                    )

            avg = total / len(window)

            if phase == "Near Field":
                self.loVal = avg

            elif phase == "Touch":
                self.touchVal = avg

            else:
                self.hiVal = avg

            print(f"{phase} average: {avg:.2f}")

        # Validate all three averages
        if not (self.loVal < self.touchVal < self.hiVal):
            print("Calibration values are not in the expected order.")
            return

        self.isCalibrated = True
        print("Fast calibration complete!")

        return

    
    def CalibrateManual(self):
            """ 
            First time calibration function. Calibration works in three phases: Force, Near field and Touch. 
            The averages of these windows will define the acceptable values. The average for Touch separates Force and 
            Near field phase. 
            """
            self.isCalibrated = False
            print(f"Calibrating {self.id}")
    
            # self.loVal = self.value
            phases = ["Near Field", "Touch", "Force"]
            interval = .25 # in seconds
            windowSize = 8 
            discardTime = 0.25
            duration = 3# num of intervals
            
            for phase in phases:

                input(f"Move into {phase} position. Press ENTER when ready...")
                window = []
                clock = time.time()
                while time.time() - clock < 3.0:

                    ReadPort()
                    elapsed = time.time() - clock

                    if discardTime <= elapsed < duration - discardTime: 
                        window.append(self.value)
                           
                print(f"{(windowSize-len(window))*interval:.1f} seconds...")
            
                if not window:
                    print(f"phase No readings collected for {phase}")
                    return

                avg = sum(window) / len(window)
                if phase == "Near Field":
                    self.loVal = avg

                elif phase == "Touch":
                    self.touchVal = avg

                else:
                    self.hiVal = avg
                
                if phase == "Force":
                    self.calibrationForce = float(input("Enter Applied force (N) or press Enter to skip \n : "))

                if not (self.loVal < self.touchVal < self.hiVal):
                    print("Calibration values are not in the expected order.") 
                    self.isCalibrated = False
                    return
                self.isCalibrated = True               
            return



    def SaveCalibration(self, filename="calibration.json"):
        """
        Saves or updates the calibration values for this sensor
        without deleting other sensors' calibration data.
        """

        if not self.isCalibrated:
            print(f"Sensor {self.id} has not been calibrated.")
            return

        # Read existing calibration data
        if os.path.exists(filename):
            with open(filename, "r") as file:
                data = json.load(file)
        else:
            data = {}

    
        data[str(self.id)] = {
            "loVal": self.loVal,
            "touchVal": self.touchVal,
            "hiVal": self.hiVal,
            "calibrationForce": getattr(self, "calibrationForce", None)
        }

   
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

        print(f"Calibration saved for sensor {self.id}.")

    
    
    def Update(self, value):
        """
            Updates the value reading and adjusts the percentage accordingly
        """
        self.value = value
        self.percent = self.getPercent(value)   

def loadCalibration(self, filename):
    if not os.path.exists(filename):
        print("File not found")
        return False
    
    with open(filename, "r") as file:
        data = json.load(file)
        
    calibration = data.get(str(self.id))
    
    if calibration is None:
        print(f"No calibration found for sensor {self.id}.")
        return False

    self.loVal = calibration["loVal"]
    self.touchVal = calibration["touchVal"]
    self.hiVal = calibration["hiVal"]
    self.calibrationForce = calibration.get("calibrationForce")

    self.isCalibrated = True

    print(f"Calibration loaded for sensor {self.id}.")
    return True
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

def OpenConnection(port=COM, baudrate=250000, timeout=.1)-> serial.Serial:
    """ Open serial connection to arduino. Retries until successful."""

    timestamp = time.time()
    printDelay = 5  # seconds
    while True:
        try:
            return serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
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
        0xAA 0xBB 2b |      n 1b    |       id 1b     | Sensor Val 3b  | *n 
        header       | sensor_count | mux | port | ch | value | capdac | ...
    """
    try:
        header1 = arduino.read(size=1)
        if header1 == b'':
            return Sensors
        if header1 == b'\xAA':
            header2 = arduino.read(size=1)
            if header2 == b'\xBB':
                payload_size = int.from_bytes(arduino.read(size=1), 'big')
                
                # Validation: reject impossible payload sizes to prevent framing errors
                if payload_size > 100:
                    return Sensors
                    
                for i in range(payload_size):
                    data = arduino.read(size=5)
                    if len(data) < 5:
                        raise ValueError("Incomplete data received.")
                    id = data[0]
                    
                    # Validation: since IDs are strictly sequential (0 to payload_size-1), 
                    # reject any ID that falls outside this bound.
                    if id >= payload_size:
                        continue
                        
                    raw_val = toSigned((data[1] << 16) | (data[2] << 8) | data[3], 24)
                    
                    capdac = data[4] & 0b1111
                    if capdac == 30:
                        print(f"Sensor {id} capdac is 31...")
                    # val = ConvertToPF(raw_val, capdac)
                    val = ConvertToPF(raw_val, capdac=capdac)
                    
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
    arduino.reset_input_buffer()
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
        
        # msg = ""
        # Create a single row list for all sensors in this timestamp
        current_time = time.perf_counter()
        elapsedTime = logger.elapsedTimeMilliseconds(startTime, current_time)
        sensorData = {}

        # for i,s in Sensors.items():
        #     if not s.isCalibrated and s.id == 0:
        #         s.Calibrate()
            
        for i,s in Sensors.items(): 
            # if not s.isCalibrated:
            #     s.Calibrate()
            #     pass
            sensorData[i] = s.value
            # Add data for each sensor
            # msg += f"{i}: {s.value:0.2f}pF "
            
        # if msg:
        #     print(msg)
            
        # Only log if we have sensor data
        if sensorData:
            logger.logData(elapsedTime, sensorData)
    