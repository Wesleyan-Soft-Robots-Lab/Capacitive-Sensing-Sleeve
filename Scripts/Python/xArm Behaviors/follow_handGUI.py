""" 
Created by: Miles Modeste
Last Updated: 7/11/2025

Description:
    uses multiple sensors and a PID controller to follow hand movement. includes GUI
"""

import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import communication as comm
import gui
from xarm.wrapper import XArmAPI

ip = '192.168.1.232'
try:
    arm = XArmAPI(ip)
except:
    pass

minThres = 1 # lowest value(%) where hand detected
targetThres = 4 # thres value(%) when arm chases towards vs moves away from hand
prevTime = time.time()
currentTime = 0.1

direction = {
    "+x":[2],
    "-x":[],
    "+y":[3],
    "-y":[1],
    "+z":[0],
    "-z":[],
}

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

def Init():
    global Sensors, Controllers, arm
    Sensors = dict[int, comm.Sensor]()
    Controllers = dict[int, PIDController]()

    arm.motion_enable(enable=True)
    arm.set_mode(0) # look into mode 4: joint velocity control
    arm.set_state(state=0)
    speed = 40
    arm.set_servo_angle(angle=[0,20.7,-37.7,0,16.9,0], speed=speed, wait=True)
    arm.set_mode(5)
    arm.set_state(0)

    #arm.motion_enable(enable=False)

    while not Sensors:
        Sensors = comm.ReadPort()

    for s in Sensors.values():
        Controllers[s.id] = PIDController(Kp=6, Ki=1, Kd=1.2, target=targetThres)

    time.sleep(1)
    return

def ToggleLock():
    if arm.state == 4:
        arm.motion_enable(enable=True)
    elif arm.state == 2:
        arm.motion_enable(enable=False)
    return

def followHand(sensors:dict[int,comm.Sensor]):
    vectors = {
        "x":0,
        "y":0,
        "z":0
    }
    for vec,arr in direction.items():
        axis = vec[1]
        op_str = vec[0]
        for i in arr:
            if (sensors[i].isCalibrated) and (minThres < sensors[i].percent):
                if op_str == "+":
                    vectors[axis] += Controllers[i].compute(sensors[i].percent, 0.1)
                elif op_str == "-":
                    vectors[axis] -= Controllers[i].compute(sensors[i].percent, 0.1)

    arm.vc_set_cartesian_velocity([vectors["x"], vectors["y"], vectors["z"], 0, 0, 0], duration=0)
    return

if __name__ == "__main__":
    Init()
    screen = gui.GUI(Sensors, arm_behaviour_callback=followHand, arm_data_callback=arm.get_servo_angle)
    screen.mainloop()