import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import communication as cm
from xarm.wrapper import XArmAPI

Sensors = dict[int, cm.Sensor]()
ip = '192.168.1.232'
arm = XArmAPI(ip)

def initArm():
    arm.motion_enable(enable=True)
    arm.set_mode(0) # look into mode 4: joint velocity control
    arm.set_state(state=0)

    speed = 40
    arm.move_gohome(speed=speed, wait=True)

    arm.set_servo_angle(angle=[0,0,-45,0,0,0], speed=speed, wait=True)

    arm.set_mode(5)
    arm.set_state(0)

    time.sleep(1)
    return

#def DistanceTo()-> int:

def followHand():
    # if sensor reading is within minimum range, move the arm towards hand in "ideal range"
    # if sensor is above maximum range, move the arm away from hand to "ideal range"
    print(Sensors["sensor_0"].percent)
    if Sensors:
        sensor1 = Sensors["sensor_0"]
        sensor2 = Sensors["sensor_1"]
        x = 0
        if (sensor1.percent > 80):
            x = 50
        elif (sensor1.percent > 50):
            x = -50
        else:
            x = 0
        if (sensor2.percent > 80):
            y = 50
        elif (sensor2.percent > 50):
            y = -50
        else:
            y = 0
        arm.vc_set_cartesian_velocity([x, y, 0, 0, 0, 0])

        return


initArm()
while True:
    Sensors = cm.ReadPort()
    followHand()