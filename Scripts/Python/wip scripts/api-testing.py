"""  
Name: Miles Modeste
Last Updated: 7/15/2025

Description:
    just testing out methods from xarm api
"""
import time
from xarm.wrapper import XArmAPI

# Globals
#SERIAL_PORT = "/dev/tty.usbmodem11301"     # Linux/Mac example
SERIAL_PORT = "COM10"                       # Windows example
BAUD_RATE = 115200 

time.sleep(1)

ip = '192.168.1.232'
arm = XArmAPI(ip)

def main():

    arm.motion_enable(enable=True)
    arm.set_mode(0) # look into mode 4: joint velocity control
    arm.set_state(state=0)

    speed = 40
    arm.move_gohome(speed=speed, wait=True)

    arm.set_servo_angle(angle=[0,0,-22.5,0,0,0], speed=speed, wait=True)
    print(arm.get_servo_angle(), arm.get_servo_angle(is_radian=True))

    arm.move_gohome(wait=True)

    print(f"state before motion enable():{arm.state}")
    arm.motion_enable(enable=False)
    print(f"after motion enable{arm.state}")

    time.sleep(20)
    return

if __name__ == "__main__":
    main()