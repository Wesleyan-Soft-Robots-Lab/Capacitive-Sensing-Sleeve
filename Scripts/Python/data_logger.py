import csv
import time
import pathlib
from pathlib import Path


def elapsedTimeMilliseconds(start, end):
    return (end - start) * 1000

def startTimer():
    return time.perf_counter()

def logData(timestamp, sensorData: dict[int, float]):
    filename = f'{time.strftime("%Y%m%d")}_SensorLog.csv'

    # Create a day-specific directory inside tests/data/cap-sensor_data
    day_dir = Path.cwd() / 'tests' / 'data' / 'cap-sensor_data' / f'{time.strftime("%Y%m%d")} '
    # Trim any accidental trailing spaces and ensure path exists
    day_dir = Path(str(day_dir).strip())
    day_dir.mkdir(parents=True, exist_ok=True)

    filepath = day_dir / filename

    # Check if file exists to determine if we need to write header
    file_exists = filepath.exists()

    sortedIDs = sorted(sensorData.keys())

    # Append rows to the CSV in the day directory
    with filepath.open('a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            header = ['Timestamp'] + [str(id) for id in sortedIDs]
            writer.writerow(header)
        row = [timestamp] + [f"{sensorData[sid]:.2f}" for sid in sortedIDs]
        writer.writerow(row)

if __name__ == "__main__":
    "Testing Only"
