import csv
import time
import pathlib
from pathlib import Path

def elapsedTimeMilliseconds(start, end):
    return (end - start) * 1000

def startTimer():
    return time.time()

def makeDir(filename):
    p = pathlib.Path(f'{time.strftime('%Y%m%d')}/')
    p.mkdir(parents = True, exist_ok=True)
    fn = filename
    filepath = p / fn
    with filepath.open("w", encoding = "utf-8") as f:
        f.write(result)

def logData(data):
    filename = f'{time.strftime("%Y%m%d")}_SensorLog.csv'
    makeDir(filename)
    # Check if file exists to determine if we need to write header
    try:
        with open(filename, 'r') as f:
            file_exists = True
    except FileNotFoundError:
        file_exists = False
    
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header only if file is new
        if not file_exists:
            writer.writerow(['Timestamp', 'SensorID', 'ValuePF'])
        writer.writerows(data)
