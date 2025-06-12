# Capacitive-Sensing-Sleeve
This repository contains documentation and up-to-date arduino and python scripts to control the xArm via capacitive sensors.

It also consolidates relevant work done in:
* [Katelyns repository](https://github.com/Wesleyan-Soft-Robots-Lab/kmccall-sensor-computation/tree/main)
* [Pattons repository](https://github.com/Wesleyan-Soft-Robots-Lab/proximity_sensing_test)

# Table of Contents
* [Directory](#folder-directory)
* [Hardware & Setup](#hardware--setup)
    * [Python Libraries](#python-libraries)
    * [Microcontroller](#arduino-mega-2560)
    * [Soft Sensor](#soft-sensor)
    * [FDC1004](#fdc1004)
        * [Components](#components)
        * [Order More](#ordering-more-chips)
        * [ProtoCentral Api](#protocentral-api)
    * [Multiplexor](#tca9548a-i2c-multiplexor)
    * [Robot Arm](#xarm5)
        * [Connecting to xArm](#connecting-to-xarm)
* [Helpful Information](#helpful-information)
* [Credits](#credits)

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
        ├─ arm.py                                       # Sensor-xArm control script
        ├─ communication.py                             # development script for everything not 
        |                                                 arm related. (eg arduino->python bit
        |                                                 communication, Sensor class methods)
```
# Hardware & Setup
## Python libraries
pip install pyserial (arduino-python comm)
pip install (xarm api??)

## Arduino MEGA 2560
+ image
+ usb cable connection
+ link to circuit diagram/image i.e. inform to reader to use slot 20 and 21 for i2c comm
+ more information abt i2c communication
To get the [FDC1004](#fdc1004) working you need to install [Protocentral api](#protocentral-api) to arduino

## Soft Sensor
+ image
+ how to construct

## FDC1004
+ image
+ katie has well documented readme about this
### Components
* R1, R2: [4.99k Ohm Surface-Mounted Resistor](https://www.digikey.com/en/products/detail/te-connectivity-passive-product/CPF0603F4K99C1/2384513)
* C1: [1 microFarad Surface-Mounted Capacitor](https://www.digikey.com/en/products/detail/yageo/CC0603KRX7R7BB105/2833611)
* C2: [.1 microFarad Surface-Mounted Capacitor](https://www.digikey.com/en/products/detail/yageo/CC0603KRX7R7BB104/302822)
* C3, C4: [51 picoFarad Surface-Mounted Capacitor](https://www.digikey.com/en/products/detail/kemet/C0603C510J5GAC7867/2200925)
### Ordering more chips
See [link](https://github.com/Wesleyan-Soft-Robots-Lab/kmccall-sensor-computation/blob/main/capacitance/README-cap.md?plain=1) on how to order more chips.
### ProtoCentral api
Easiest way is to open ArduinoIDE and in the library manager search for "ProtoCentral FDC1004 Capacitive Sensor Library" by ProtoCentral.
[src](https://github.com/Protocentral/ProtoCentral_fdc1004_breakout/tree/master/src)
### [More Info (pdf)](https://www.ti.com/lit/ds/symlink/fdc1004.pdf?ts=1726805458775)

## TCA9548A I2C Multiplexor
+ image
+ link to more info

## xArm5
* [api](https://github.com/xArm-Developer/xArm-Python-SDK/blob/master/doc/api/xarm_api.md)
* [User manual](https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf)
### Connecting to xArm:
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
    
    #### Mac
    1. ...
3. ... 

# Helpful Information
* [Measuring a Single Capcitor](https://github.com/Wesleyan-Soft-Robots-Lab/kmccall-sensor-computation/blob/main/capacitance/README-cap.md?plain=1#additional-resources)
# Credits