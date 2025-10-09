""" 
Name: Miles Modeste
Date Created: 6/11/2025
Last Updated: 6/30/2025

Description:
  Record data from sensors as csv and display it

"""
import sys
import os
import time
import pandas as pd
import csv
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import Scripts.Python.outdated.communication as comm

def DisplayData():
    #calculate std of each sensor
    stds = df.groupby('id')['value'].std().reset_index()

    print("Standard deviations of each sensor:")
    print(stds)

    csvFile = os.path.join(fileFolder, 'standard_dev.csv')

    code = fileName.split('_')[-1][0]  
    row = [code, stds['value'].iloc[0], stds['value'].iloc[1]]
    with open(csvFile, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)
        
    # plot data
    plt.figure(figsize=(10, 6))
    for sensor_id in df['id'].unique():
        sensor_data = df[df['id'] == sensor_id]
        plt.plot(sensor_data['timeStamp'], sensor_data['value'], label=f'Sensor {sensor_id}')
    plt.xlabel('Time (s)')
    plt.ylabel('Value (fF)')
    plt.title('Sensor Data Over Time')
    plt.grid(True)

    plt.legend()
    plt.show()

def init():
    global fileFolder, fileName, filePath, runTime, Sensors

    fileName = input("File name: ")
    fileFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'off-arm_data'))
    filePath = os.path.join(fileFolder,fileName)
    #runTimeInpt = input("Run time (min) *enter for default(1)*: ")
    runTime = 180

    Sensors = dict[int, comm.Sensor]()

if __name__ == "__main__":
    init()
    """ # wait for sensors to be ready & calibrated
    while Sensors == {} or not all(s.isCalibrated for s in Sensors.values()):
        Sensors = cm.ReadPort()
        for s in Sensors.values():
            if not s.isCalibrated:
                s.Calibrate() """
    
    print("2 seconds until recording starts... REMOVE HAND!")
    start = time.time()
    while True:
        if time.time() - start > 2:
            break
        Sensors = comm.ReadPort()

    print("Starting data recording...")

    start = time.time()
    rows = []
    while (time.time() - start < runTime):
        Sensors = comm.ReadPort()
        t = time.time() - start
        for s in Sensors.values():
            rows.append({
                'timeStamp': t,
                'id': s.id,
                'value': s.value,
                'percent': s.percent
                })
    df = pd.DataFrame(rows)
    df.to_csv(filePath + '.csv', index=False)
    print(f"Data saved to {filePath}.csv")
    
    DisplayData()

    sys.exit(0)

    