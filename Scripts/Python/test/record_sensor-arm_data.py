""" 
Name: Miles Modeste
Last Updated: 7/11/2025

Description:
  Record data sensors and arm position as csv
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import communication as comm
import gui
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','xArm_Behaviors')))
import follow_handGUI

def init():
    global fileFolder, fileName, filePath, Sensors

    fileName = input("File name: ")
    fileFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'off-arm_data'))
    filePath = os.path.join(fileFolder,fileName)

    

if __name__=="__main__":
    init()
    screen = gui.GUI(Sensors)