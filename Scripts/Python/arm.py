"""  
Name: Miles Modeste
Date Created: 6/11/2025
Last Updated: 6/12/2025

Description:
    This is my first attempt at controlling the xArm using Arduino.

TODO:
    - Saftey feature to not be able to read measurements until sensor hi/lo has been
      calibrated. (Hard Press to calibrate)
    - Add sensor method for calculating percent readings to standardize thresholds
      (total percentage, and percent increase/decrease)
    - Explore using arm.set_mode(4) which is motor velocity control mode...allegedly

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

# Globals
SERIAL_PORT = "/dev/tty.usbmodem11301"     # Linux/Mac example
# SERIAL_PORT = "COM10"                       # Windows example
BAUD_RATE = 115200 

arduino = serial.Serial(SERIAL_PORT, BAUD_RATE)
time.sleep(1)

ip = '192.168.1.232'
arm = XArmAPI(ip)

Sensors = dict[int, Sensor]()

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

def main():

    arm.motion_enable(enable=True)
    arm.set_mode(0) # look into mode 4: joint velocity control
    arm.set_state(state=0)

    speed = 40
    arm.move_gohome(speed=speed, wait=True)

    arm.set_servo_angle(angle=[0,0,-90,0,0,0], speed=speed, wait=True)
    print(arm.get_servo_angle(), arm.get_servo_angle(is_radian=True))

    arm.move_gohome(wait=True)

    while True:
        ReadPort()
        print(Sensors["sensor_0"].value)
        if Sensors:
            try:
                if Sensors["sensor_0"].value <= 18000:
                    arm.move_gohome()
                    #print(arm.get_sergo_angle())
                else:
                    arm.set_servo_angle(angle=[0,0,-90,0,0,0], speed=speed)
                    #print(arm.get_sergo_angle())
                    
            except ValueError:
                print("Invalid input received!")

    arm.disconnect()
    return

if __name__ == "__main__":
    main()