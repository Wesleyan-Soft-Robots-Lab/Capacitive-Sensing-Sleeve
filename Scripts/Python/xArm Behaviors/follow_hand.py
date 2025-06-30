""" 
Created by: Miles Modeste
Last Updated: 6/26/2025

Description:
  uses multiple sensors and a PID controller to follow hand movement.  
"""

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

minThres = 1.5 # lowest value(%) where hand detected
targetThres = 9 # thres value(%) when arm chases towards vs moves away from hand
prevTime = time.time()
currentTime = 0.1

armVelocity = [0,0,0]

class PIDController:
    def __init__(self, Kp, Ki, Kd, target):
        self.Kp = Kp  # Proportional gain: controls responsiveness/stiffness
        self.Ki = Ki  # Integral gain: slowdown before target/how close to target value
        self.Kd = Kd  # Derivative gain: controls damping
        self.target = target # target value

        self.previous_error = 0
        self.integral = 0

    def compute(self, process_variable, dt):
        """  dt : delta time """
        error = self.target - process_variable
        # Proportional - present
        P_out = self.Kp * error
        # Integral - past 
        self.integral += error * dt
        I_out = self.Ki * self.integral
        # Derivative - future
        #print(f"({error}-{self.previous_error}) / {dt}")
        derivative = (error - self.previous_error) / dt
        D_out = self.Kd * derivative

        self.previous_error = error

        output = P_out + I_out + D_out
        return output

def init():
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

def followHand():
    global prevTime, currentTime, pid
    xv, yv, zv = 0, 0, 0

    if Sensors:
        sensor1 = Sensors[0]
        if (not sensor1.isCalibrated):
            sensor1.Calibrate()
            pid = PIDController(Kp=5, Ki=0, Kd=1.2, target=targetThres)
            time.sleep(1)
        
        if ((minThres < sensor1.percent)):
            """ currentTime = time.time()
            dt = currentTime - prevTime
            prevTime = currentTime """
            yv = pid.compute(sensor1.percent, 0.1)

        print(f"{sensor1.percent} || {yv}")
        arm.vc_set_cartesian_velocity([xv, yv, zv, 0, 0, 0], duration=0)

        return

if __name__ == "__main__":
    init()
    while True:
        Sensors = cm.ReadPort()
        followHand()