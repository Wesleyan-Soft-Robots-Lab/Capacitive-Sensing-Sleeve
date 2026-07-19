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
import fast_communication as comm
from xarm.wrapper import XArmAPI

ip = '192.168.1.232'
try:
    arm = XArmAPI(ip)
except:
    pass

minThres = 1 # lowest value(%) where hand detected
targetThres = 1.5 # thres value(%) when arm chases towards vs moves away from hand
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
        
        # Integral - past (with Anti-Windup clamp)
        self.integral += error * dt
        # Clamp integral to prevent it from growing too large (integral windup)
        # Assuming maximum safe I_out is around 20
        max_i = 20.0
        if self.Ki > 0:
            self.integral = max(-max_i/self.Ki, min(max_i/self.Ki, self.integral))
            
        I_out = self.Ki * self.integral
        
        # Derivative - future
        derivative = (error - self.previous_error) / dt
        D_out = self.Kd * derivative

        self.previous_error = error

        output = P_out + I_out + D_out
        
        # Reset integral if we cross the zero-error point to stop overshooting
        if (self.previous_error > 0 and error < 0) or (self.previous_error < 0 and error > 0):
            self.integral = 0
            
        return output

def Init():
    global Sensors, Controllers
    Sensors = dict[int, comm.Sensor]()
    Controllers = dict[int, PIDController]()
    [int, [comm.Sensor, PIDController, str]]
    Initialized = False

    arm.motion_enable(enable=True)
    arm.set_mode(0) # look into mode 4: joint velocity control
    arm.set_state(state=0)

    speed = 40
    arm.move_gohome(speed=speed, wait=True)

    arm.set_servo_angle(angle=[0,20.7,-37.7,0,16.9,0], speed=speed, wait=True)

    arm.set_mode(5)
    arm.set_state(0)

    time.sleep(1)
    while not Initialized:
        Sensors = comm.ReadPort()
        for idx in Sensors:
            if not Sensors[idx].isCalibrated and Sensors[idx].id == 0:
                Sensors[idx].Calibrate()
                Controllers[idx] = PIDController(Kp=15, Ki=1, Kd=1.2, target=targetThres)
            # if all(s.isCalibrated for s in Sensors.values()):
                Initialized = True
    
    print("Initialization Complete...") 
    return

def followHand():
    xv, yv, zv = 0, 0, 0

    # if Sensors:
    #     sensor1 = Sensors[0]
        # if (not sensor1.isCalibrated):
        #     sensor1.Calibrate()
        #     pid = PIDController(Kp=5, Ki=0, Kd=1.2, target=targetThres)
        #     time.sleep(1)
        
        # if ((minThres < sensor1.percent)):
        #     zv = pid.compute(sensor1.percent, 0.1)

        # print(f"{sensor1.percent} || {xv}, {yv}, {zv}") 
    print(f"{Sensors[0].percent} | {Sensors[0].value} | ")
    if ((minThres < Sensors[0].percent)):
        yv = -Controllers[0].compute(Sensors[0].percent, 0.1)
        
        # Margin of Error (Deadband): Prevents the arm from jittering back and forth
        # when it is already very close to the target threshold.
        margin_of_error = 0.3
        current_error = Controllers[0].target - Sensors[0].percent
        if abs(current_error) <= margin_of_error:
            yv = 0
            Controllers[0].integral = 0 # Prevent small errors from building up
            print(f"Holding steady! (Error: {current_error:.2f})")
        else:
            # clamp the velocity to safe limits in case error is huge
            yv = max(-150, min(150, yv))
            if yv > 0:
                print(f"Moving CLOSER at speed {yv:.2f} (Error: {current_error:.2f})")
            else:
                print(f"Moving AWAY at speed {yv:.2f} (Error: {current_error:.2f})")
        # if ((minThres < Sensors[2].percent)):
        #     xv += Controllers[2].compute(Sensors[2].percent, 0.1)
        # if ((minThres < Sensors[0].percent)):
        #     zv += Controllers[0].compute(Sensors[0].percent, 0.1)

    arm.vc_set_cartesian_velocity([xv, yv, zv, 0, 0, 0], duration=0)

    return

if __name__ == "__main__":
    Init()
    while True:
        Sensors = comm.ReadPort()
        followHand()