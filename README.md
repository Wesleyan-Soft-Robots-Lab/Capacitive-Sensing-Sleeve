# Capacitive-Sensing-Sleeve
This repository contains documentation and up-to-date arduino and python scripts to control the xArm via capacitive sensors.

It also consolidates relevant work done in:
* [Katelyns repository](https://github.com/Wesleyan-Soft-Robots-Lab/kmccall-sensor-computation/tree/main)
* [Pattons repository](https://github.com/Wesleyan-Soft-Robots-Lab/proximity_sensing_test)

# Table of Contents
* [Directory](#folder-directory)
* [Hardware & Setup](#hardware--setup)
    * [Soft Sensor](#soft-sensor)
    * [Microcontroller](#arduino-mega-2560)
    * [FDC1004](#fdc1004)
    * [Multiplexor](#tca9548a-i2c-multiplexor)
    * [Robot Arm](#xarm5)
        * [Connecting to xArm](#connecting-to-xarm)

# Folder Directory
(subject to change)
```
├─ README.md                <-- You are Here
├─ Documentation                                        # Folder for information and documentation
├─ Scripts                                              # Folder for all code
    ├─ Arduino                                          # Folder with C++            
        ├─ Demo-singleCap/ Demo-singleCap.ino           # tutorial script for visualizing cap sensors
        |                                                 in the serial plotter
        ├─ multiCap/ multiCap.ino                       # current script being used to read multiple
        |                                                 capacitive sensors 
    ├─ Python                                           # Folder with Python code
        ├─ arm.py                                       # code to control arm
        ├─ communication.py                             # python code to read from the arduino
```
# Hardware & Setup
## Soft Sensor
    + image
    + how to construct
## Arduino MEGA 2560
    + image
    + usb cable connection
    + link to circuit diagram/image i.e. inform to reader to use slot 20 and 21 for i2c comm
    + more information abt i2c communication
## FDC1004
    + image
    + link to pdf info
## TCA9548A I2C Multiplexor
    + image
    + link to more info
## xArm6
#### <u> Connecting to xArm (Using the ufactory studio app)</u>:
### Configuring machine:
1. Double check all cables are properly connected and "Emergency Stop" button is up. All leds should be lit (Flickering LAN leds are OK, it's working) There is a sticker with an IP address labeled **192.168.232** !Remember where to find this!
2. Configure IP Address: (someone who hasn't connected to the arm b4, please confirm if step is necessary. I think you might only need to wait for the 3 beeps for the server to get ready).
    #### Windows 11:
    1. Open your **Control Panel**
    2. Navigate to: <u>Network and Internet</u> > <u>Network and Sharing Center</u>
    3. On the lefthand side click **Change adapter settings**
    4. Right click on the correct ethernet device and select **Properties** in the dropdown
    5. Scroll down and select <u>Internet Protocol Version 4 (IPv4)</u>, then hit **Properties**
    6. Set IP: **192.168.1.x**; and Subnet Mask: **255.255.255.0** (x can be anything from 0-255. **! Do NOT choose same ip as sticker !**)
    7. Hit **OK** and **Close** to confirm settings
    
    #### Mac:
    ## Getting a feel through Ufactory studion GUI:
    1. Connect the ethernet cable from the arm set up to your computer
    2. navigate to system settings --> Network --> Ethernet.
    3. Select **<u>USB 10/100/1000LAN</u>** --> click **details** --> **TCP/IP**, and set **<u>configure IPv4<\u>** to **manually**
    4. Set IP: **192.168.1.x**; and Subnet Mask: **255.255.255.0** (x can be anything from 0-255. **! Do NOT choose same ip as sticker !**), confirm settings.

### Download and set up UFactory studio app:
   - [download ufactory studio app on your machine](https://www.ufactory.us/ufactory-studio)
   - open and enter 192.168.1.232(IP address found on the arm block sticker) onto the search bar
   - click connect, and explore the options of arm controll 
   **NB MAC USERS :**The studio app may flag as unsafe and fail to open the first time. Go to system settings, scroll down and click privacy and security. Then scroll to the bottom and you will see the app listed as an unsafe app that tried to open, click allow anyway

#### <u> Connecting to xArm (Python arm.py script)</u>:
###



