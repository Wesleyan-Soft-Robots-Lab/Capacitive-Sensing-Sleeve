# Capacitive-Sensing-Sleeve
This repository contains documentation and up-to-date arduino and python scripts to control the xArm via capacitive sensors.

It also consolidates relevant work done in:
* [Katelyns repository](https://github.com/Wesleyan-Soft-Robots-Lab/kmccall-sensor-computation/tree/main)
* [Pattons repository](https://github.com/Wesleyan-Soft-Robots-Lab/proximity_sensing_test)

# Table of Contents
* [Directory](#folder-directory)
<<<<<<< Updated upstream
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
=======
* [Hardware Components](#hardware)  
   * [Capacitive Sensor](#capacitive-sensor)
   * [Microcontroller](#arduino-mega-2560)
   * [FDC1004](#fdc1004)
   * [Multiplexor](#pca9548a-i2c-multiplexor)
   * [Robot Arm](#xarm6)
* [Setting Up Hardware](#hardware-set-up)
* [Software]
   * [Arduino]
      * [ProtoCentral Api](#protocentral-api)
   * [Python Libraries](#python-libraries)
      * [xArm SKD]
   * [src guide]
* [Construction](#construction)
   * [Sensor Patch]
   * [Shield]
   * [Soldering FDC]
   * [Sleeve]
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
# Hardware & Setup
## Python libraries
pip install pyserial (arduino-python comm)
pip install (xarm api??)

## Arduino MEGA 2560
=======
## Hardware
### Capacitive Sensor
+ add image
+ add description

learn how to create your own patch (here)[link to construction document]
### Arduino MEGA 2560
>>>>>>> Stashed changes
+ image
+ description ()
+ link to katies repo for connecting just cap sensor and microcontroller
+ more information abt i2c communication
<<<<<<< Updated upstream
To get the [FDC1004](#fdc1004) working you need to install [Protocentral api](#protocentral-api) to arduino

## Soft Sensor
+ image
+ how to construct
=======
+ link to arduino specs
>>>>>>> Stashed changes

## FDC1004
+ image
<<<<<<< Updated upstream
+ katie has well documented readme about this
### Components
=======
+ description

katie has well documented readme about this
#### Components
>>>>>>> Stashed changes
* R1, R2: [4.99k Ohm Surface-Mounted Resistor](https://www.digikey.com/en/products/detail/te-connectivity-passive-product/CPF0603F4K99C1/2384513)
* C1: [1 microFarad Surface-Mounted Capacitor](https://www.digikey.com/en/products/detail/yageo/CC0603KRX7R7BB105/2833611)
* C2: [.1 microFarad Surface-Mounted Capacitor](https://www.digikey.com/en/products/detail/yageo/CC0603KRX7R7BB104/302822)
* C3, C4: [51 picoFarad Surface-Mounted Capacitor](https://www.digikey.com/en/products/detail/kemet/C0603C510J5GAC7867/2200925)
<<<<<<< Updated upstream
### Ordering more chips
See [link](https://github.com/Wesleyan-Soft-Robots-Lab/kmccall-sensor-computation/blob/main/capacitance/README-cap.md?plain=1) on how to order more chips.
### ProtoCentral api
Easiest way is to open ArduinoIDE and in the library manager search for "ProtoCentral FDC1004 Capacitive Sensor Library" by ProtoCentral.
[src](https://github.com/Protocentral/ProtoCentral_fdc1004_breakout/tree/master/src)
### [More Info (pdf)](https://www.ti.com/lit/ds/symlink/fdc1004.pdf?ts=1726805458775)

## TCA9548A I2C Multiplexor
+ image
+ link to more info

## xArm6
=======

#### -
+ add link to construction document
#### Ordering more chips
See [link](https://github.com/Wesleyan-Soft-Robots-Lab/kmccall-sensor-computation/blob/main/capacitance/README-cap.md) about ordering more chips.
#### [More Info (pdf)](https://www.ti.com/lit/ds/symlink/fdc1004.pdf?ts=1726805458775)


### PCA9548A I2C Multiplexor
+ image
+ description (key phrase: we are using daisy chaining(link to definition))
+ [buy](https://www.adafruit.com/product/5626)
+ [See more](https://learn.adafruit.com/adafruit-pca9548-8-channel-stemma-qt-qwiic-i2c-multiplexer/pinouts)


### xArm6
+ image
>>>>>>> Stashed changes
* [api](https://github.com/xArm-Developer/xArm-Python-SDK/blob/master/doc/api/xarm_api.md)
* [User manual](https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf)
### <u> Connecting to xArm (Using the ufactory studio app)</u>:
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
    3. Select **<u>USB 10/100/1000LAN</u>** --> click **details** --> **TCP/IP**, and set **<u>configure IPv4</u>** to **manually**
    4. Set IP: **192.168.1.x**; and Subnet Mask: **255.255.255.0** (x can be anything from 0-255. **! Do NOT choose same ip as sticker !**), confirm settings.

### Download and set up UFactory studio app:
   - [download ufactory studio app on your machine](https://www.ufactory.us/ufactory-studio)
   - open and enter 192.168.1.232(IP address found on the arm block sticker) onto the search bar
   - click connect, and explore the options of arm controll 
   **NB MAC USERS :**The studio app may flag as unsafe and fail to open the first time. Go to system settings, scroll down and click privacy and security. Then scroll to the bottom and you will see the app listed as an unsafe app that tried to open, click allow anyway

<<<<<<< Updated upstream
#### <u> Connecting to xArm (Python arm.py script)</u>:
###
=======
## Hardware Setup
1. Follow diagram for connecting wires: insert diagram
2. if you are daisychaining multiplexors see [link](https://learn.adafruit.com/adafruit-pca9548-8-channel-stemma-qt-qwiic-i2c-multiplexer/pinouts#address-pins-3129199) about soldering address pins
## Software Guide
The Scripts folder is sorted into arduino code and python code. For the arduino, the only two significant scripts are [multiCap.ino](Scripts/Arduino/multiCap/multiCap.ino) and [fast_multiCap.ino](Scripts/Arduino/fast_multiCap/fast_multiCap.ino). 

For running the newer python scripts the arduino uses [fast_multiCap.ino](Scripts/Arduino/fast_multiCap/fast_multiCap.ino)
For arduino libraries you must use Protocentrals fdc1004


>>>>>>> Stashed changes

# Helpful Information
* [Measuring a Single Capcitor](https://github.com/Wesleyan-Soft-Robots-Lab/kmccall-sensor-computation/blob/main/capacitance/README-cap.md?plain=1#additional-resources)
<<<<<<< Updated upstream
# Credits
=======
* [xArm sdk](https://github.com/xArm-Developer/xArm-Python-SDK)
## Expanding the Project
# Credits
>>>>>>> Stashed changes
