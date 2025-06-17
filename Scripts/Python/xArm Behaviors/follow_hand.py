import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import communication as cm
from xarm.wrapper import XArmAPI

Sensors = dict[int, cm.Sensor]()
ip = '192.168.1.232'
try:
    arm = XArmAPI(ip)
except:
    pass

maxThres = 20 # closest value(%) where hand recognized 
minThres = -3 # farthest value(%) where hand recognized
threshold = 5 # thres value(%) when arm chases towards vs moves away from hand
m = 10 #slope
def CalculateVelocity(percent: float)-> float:
    #leanear fx to calc velocity
    #TODO: experiment with x^3 velocity
    # y = mx + b s.t. 0 = m*threshold+b
    b = -(-m*threshold)
    return -m*percent+b

def initArm():
    arm.motion_enable(enable=True)
    arm.set_mode(0) # look into mode 4: joint velocity control
    arm.set_state(state=0)

    speed = 40
    arm.move_gohome(speed=speed, wait=True)

    arm.set_servo_angle(angle=[0,20.7,-37.7,0,16.9,0], speed=speed, wait=True)

    arm.set_mode(5)
    arm.set_state(0)

    time.sleep(1)
    return

#def DistanceTo()-> int:

def followHand():
    # if sensor reading is within minimum range, move the arm towards hand in "ideal range"
    # if sensor is above maximum range, move the arm away from hand to "ideal range"
    if Sensors:
        sensor1 = Sensors["sensor_0"]
        if (not sensor1.isCalibrated):
            sensor1.Calibrate()
        sensor2 = Sensors["sensor_1"]
        zv = 0
        if ((minThres < sensor1.percent) and (sensor1.percent < maxThres)):
            zv = CalculateVelocity(sensor1.percent)
        print(sensor1.percent)
        
        arm.vc_set_cartesian_velocity([0, 0, zv, 0, 0, 0])

        return

if __name__ == "__main__":
    initArm()
    while True:
        Sensors = cm.ReadPort()
        followHand()