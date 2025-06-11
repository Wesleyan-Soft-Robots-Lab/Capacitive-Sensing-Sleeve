# Capacitive-Sensing-Sleeve
This repository contains documentation and up-to-date arduino and python scripts to control the xArm via capacitive sensors.

It also consolidates relevant work done in:
* [Katelyns repository](https://github.com/Wesleyan-Soft-Robots-Lab/kmccall-sensor-computation/tree/main)
* [Pattons repository](https://github.com/Wesleyan-Soft-Robots-Lab/proximity_sensing_test)

# Table of Contents
* [Directory](#directory)
* [Hardware Used](#hardware)
    * [Connecting to xArm](#configuring-the-xarm-ip-address)

# Directory
```
├─ README.md                <-- You are Here
├─ Documentation                                        # Folder for information and documentation
├─ Scripts                                              # Folder for all code
    ├─ Arduino                                          # Folder with C++            
        ├─ Demo-singleCap/ Demo-singleCap.ino           # tutorial script for visualizing cap sensors
        |                                                 in the serial plotter
        ├─ multiCap/ multiCap.ino                       # current script being used to run
    ├─ Python
        ├─ arm.py
        ├─ communication.py
```
# Hardware
## Configuring the xArm IP Address

pip install xarm-python-sdk