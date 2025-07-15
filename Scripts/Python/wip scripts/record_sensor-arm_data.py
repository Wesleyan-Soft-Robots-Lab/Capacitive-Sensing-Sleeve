""" 
Name: Miles Modeste
Last Updated: 7/11/2025

Description:
  Record data sensors and arm position as csv
"""
import sys
import os
import time
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import communication as comm
import gui
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','xArm Behaviors')))

def init():
    global fileFolder, fileName, filePath, Sensors

    fileName = input("File name: ")
    fileFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'off-arm_data'))
    filePath = os.path.join(fileFolder,fileName)

def RecordPoint(df: pd.DataFrame, sensorsInp:dict[int,comm.Sensor]=None, armData:list=None):
    
    row = []
    t = time.time()
    row.append({"timeStamp": t})

    for k,v in sensorsInp.items():
        row.append({f"sensor_{k}": [v.value, v.percent, v.hiVal, v.loVal]})

    if armData != None:
        row.append({"arm_pos": armData})

    df.loc[len(df)] = row

if __name__=="__main__":
    init()
    screen = gui.GUI(Sensors)