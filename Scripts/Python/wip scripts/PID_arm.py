""" 
Created by: Miles Modeste
Date Created: 6/26/2025
Last Updated: 6/26/2025

Description:
  test script for PID controller integration with xArm using position feedback.
  Mainly for tuning PID values.  
"""

import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#import gui
from xarm.wrapper import XArmAPI

ip = '192.168.1.232'
try:
    arm = XArmAPI(ip)
except:
    pass

xv, yv, zv = 0, 0, 0
pid = None
setPoint = 150  

armActive = False
sensorsReady = False

class PIDController:
    def __init__(self, Kp, Ki, Kd, target):
        self.Kp = Kp  # Proportional gain: controls responsiveness/stiffness
        self.Ki = Ki  # Integral gain: slowdown before target/how close to target value
        self.Kd = Kd  # Derivative gain: controls damping
        self.target = target # target value

        self.previous_error = 0
        self.integral = 0

    def compute(self, process_variable, dt=0.1):
        """  
        dt : delta time
        returns: velocity
        """
        error = self.target - process_variable
        # Proportional - present
        P_out = self.Kp * error
        # Integral - past 
        self.integral += error * dt
        I_out = self.Ki * self.integral
        # Derivative - future
        derivative = (error - self.previous_error) / dt
        D_out = self.Kd * derivative

        self.previous_error = error

        output = P_out + I_out + D_out
        return output

def init():
    global pid
    arm.motion_enable(enable=True)
    arm.set_mode(0) # look into mode 4: joint velocity control
    arm.set_state(state=0)

    speed = 40
    arm.move_gohome(speed=speed, wait=True)

    arm.set_servo_angle(angle=[0,20.7,-37.7,0,16.9,0], speed=speed, wait=True)

    arm.set_mode(5) # look into mode 4: joint velocity control
    arm.set_state(state=0)
    pid = PIDController(Kp=1, Ki=0, Kd=0.9, target=setPoint)
    time.sleep(1)
    return

def followHand():
    global xv,yv,zv, pid
    _,pos = arm.get_position()
    x,y,z = pos[0:3]
    
    yv = pid.compute(y, 0.1)

    arm.vc_set_cartesian_velocity([xv, yv, zv, 0, 0, 0], duration=0)

    return

if __name__ == "__main__":
    init()
    while True:
        followHand()