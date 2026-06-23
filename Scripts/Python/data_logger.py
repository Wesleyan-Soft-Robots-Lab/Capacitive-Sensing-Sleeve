import csv
import time
from pathlib import Path

_current_session_filepath = None

def elapsedTimeMilliseconds(start, end):
    return (end - start) * 1000

def startTimer():
    return time.perf_counter()

def _get_session_filepath():
    """Generates and caches the filepath with an auto-incrementing test number."""
    global _current_session_filepath
    
    # If the filepath was already generated for this run, reuse it
    if _current_session_filepath is not None:
        return _current_session_filepath

    date_str = time.strftime("%Y%m%d")
    day_dir = Path.cwd() / 'tests' / 'data' / 'cap-sensor_data' / date_str
    
    day_dir = Path(str(day_dir).strip())
    day_dir.mkdir(parents=True, exist_ok=True)

    # Count existing test files in today's directory to determine the next test number
    existing_files = list(day_dir.glob(f"{date_str}_*_NOSH_STICK_2cm_SensorLog.csv"))
    test_number = len(existing_files) + 1

    filename = f"{date_str}_{test_number}_NOSH_STICK_2cm_SensorLog.csv"
    _current_session_filepath = day_dir / filename

    return _current_session_filepath

def logData(timestamp, sensorData: dict[int, float]):
    filepath = _get_session_filepath()

    file_exists = filepath.exists()

    sortedIDs = sorted(sensorData.keys())

    with filepath.open('a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            header = ['Timestamp'] + [str(id) for id in sortedIDs]
            writer.writerow(header)
            
        row = [timestamp] + [f"{sensorData[sid]:.2f}" for sid in sortedIDs]
        writer.writerow(row)