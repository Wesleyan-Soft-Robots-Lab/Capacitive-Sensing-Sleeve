import csv
import time
from pathlib import Path

_current_session_filepath = None
_current_file = None
_csv_writer = None

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
    existing_files = list(day_dir.glob(f"{date_str}_*_NOSH_BIGALUM_1cm_SensorLog.csv"))
    test_number = len(existing_files) + 1

    filename = f"{date_str}_{test_number}_NOSH_BIGALUM_1cm_SensorLog.csv"
    _current_session_filepath = day_dir / filename

    return _current_session_filepath

_fieldnames = None

def logData(timestamp, sensorData: dict[int, float]):
    global _current_file, _csv_writer, _current_session_filepath, _fieldnames
    filepath = _get_session_filepath()

    if _current_file is None or _current_file.closed:
        file_exists = filepath.exists()
        _current_file = filepath.open('a', newline='')
        _csv_writer = csv.writer(_current_file)
        if not file_exists:
            _fieldnames = sorted(sensorData.keys())
            header = ['Timestamp'] + [str(id) for id in _fieldnames]
            _csv_writer.writerow(header)
        else:
            _fieldnames = sorted(sensorData.keys())

    if _fieldnames is None:
        _fieldnames = sorted(sensorData.keys())

    # Only log the exact fields defined in the header
    row = [timestamp] + [f"{sensorData.get(sid, 0.0):.2f}" for sid in _fieldnames]
    _csv_writer.writerow(row)
    _current_file.flush()