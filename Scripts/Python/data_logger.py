import csv
import time

def elapsedTimeMilliseconds(start, end):
    return (end - start) * 1000

def startTimer():
    return time.time()

def logData(data):
    filename = f'{time.strftime("%Y%m%d")}_SensorLog.csv'
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
