import csv
import time

def log_data(sensor_data):
    with open (f'{time.strftime("%Y%m%d")}_SensorLog.csv', 'w', newline='') as csvfile:
        fieldnames = ['Timestamp', 'SensorID', 'ValuePF']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()