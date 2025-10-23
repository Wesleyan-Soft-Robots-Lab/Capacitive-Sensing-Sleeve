import csv
import time
import pathlib
from pathlib import Path

def elapsedTimeMilliseconds(start, end):
    return (end - start) * 1000

def startTimer():
    return time.time()

def logData(data):
    filename = f'{time.strftime("%Y%m%d")}_SensorLog.csv'

    # Create a day-specific directory inside tests/data/cap-sensor_data
    day_dir = Path.cwd() / 'tests' / 'data' / 'cap-sensor_data' / f'{time.strftime("%Y%m%d")} '
    # Trim any accidental trailing spaces and ensure path exists
    day_dir = Path(str(day_dir).strip())
    day_dir.mkdir(parents=True, exist_ok=True)

    filepath = day_dir / filename

    # Check if file exists to determine if we need to write header
    file_exists = filepath.exists()

    # Append rows to the CSV in the day directory
    with filepath.open('a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Timestamp', 'SensorID', 'ValuePF'])
        writer.writerows(data)

if __name__ == "__main__":
    "Testing Only"
