import time
import csv
import os
import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi
import glob
from pathlib import Path

class RealTimeButterworth:
    """
    A class that implements a real-time Butterworth filter using lfilter_zi for state maintenance.
    Supports filtering multi-channel data sequentially (sample-by-sample).
    """
    def __init__(self, cutoff_freq, fs, order=4, num_channels=2):
        self.cutoff_freq = cutoff_freq
        self.fs = fs
        self.order = order
        self.num_channels = num_channels
        nyq = 0.5 * fs
        self.b, self.a = butter(order, cutoff_freq / nyq, btype='low', analog=False)
        # Calculate the initial state for the filter
        zi = lfilter_zi(self.b, self.a)
        # Expand zi for multiple channels if needed
        if num_channels > 1:
            self.zi = np.repeat(zi[:, np.newaxis], num_channels, axis=1)
        else:
            self.zi = zi

    def process(self, x):
        """
        Process a single sample across channels.
        x should be a list or 1D array of shape (num_channels,).
        """
        x_in = np.atleast_2d(x)
        if not hasattr(self, 'initialized'):
            # Multiply initial state zi by the first value of each channel to avoid massive startup transients
            if self.num_channels == 1:
                self.zi = self.zi * x_in[0, 0]
            else:
                self.zi = self.zi * x_in
            self.initialized = True
            
        y, self.zi = lfilter(self.b, self.a, x_in, axis=0, zi=self.zi)
        return y[0]


def tail_and_filter_csv(csv_path, fs, cutoff_freq, exclude_cols=None):
    """
    Tails a CSV file being actively written to (e.g., by fast_communication.py)
    and applies the RealTimeButterworth filter to the incoming data stream,
    saving the filtered output to a new CSV file in real-time.
    """
    if exclude_cols is None:
        exclude_cols = []
        
    print(f"Waiting for {csv_path} to be created...")
    while not os.path.exists(csv_path):
        time.sleep(0.5)
        
    freq_label = f"{cutoff_freq:.2f}Hz"
    output_filename = csv_path.replace('.csv', f'_LIVE_RT_FILTERED_{freq_label}.csv')
    
    with open(csv_path, 'r') as infile, open(output_filename, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        header = None
        while not header:
            header = next(reader, None)
            if not header:
                time.sleep(0.1)
                
        writer.writerow(header)
        outfile.flush()
        
        sensor_indices = [i for i, col in enumerate(header) if col not in exclude_cols]
        sensor_ids = [header[i] for i in sensor_indices]
        
        rt_filter = RealTimeButterworth(cutoff_freq, fs, order=4, num_channels=len(sensor_ids))
        print(f"Started real-time filtering from: {csv_path}")
        print(f"Writing filtered data to:      {output_filename}")
        try:
            while True:
                # Read new lines as they are written
                line = next(reader, None)
                if line:
                    try:
                        # Extract raw values
                        raw_values = [float(line[i]) for i in sensor_indices]
                        
                        # Process through real-time filter
                        filtered_values = rt_filter.process(raw_values)
                        
                        out_row = list(line)
                        for idx, val in zip(sensor_indices, filtered_values):
                            out_row[idx] = f"{val:.4f}"
                            
                        writer.writerow(out_row)
                        outfile.flush()
                        
                    except (ValueError, IndexError):
                        pass # Skip lines with invalid/incomplete numeric data
                else:
                    time.sleep(0.01)
        except KeyboardInterrupt:
            print("\nStopped real-time filtering.")

def get_latest_sensor_log():
    """Finds the most recently created CSV file by data_logger.py in today's directory."""
    date_str = time.strftime("%Y%m%d")
    day_dir = Path.cwd() / 'tests' / 'data' / 'cap-sensor_data' / date_str
    
    if not day_dir.exists():
        return None
        
    csv_files = list(day_dir.glob("*_SensorLog.csv"))
    
    csv_files = [f for f in csv_files if "LIVE_RT_FILTERED" not in f.name]
    
    if not csv_files:
        return None
        
    latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
    return str(latest_file)

if __name__ == "__main__":
    COLUMNS_TO_IGNORE = ['Timestamp'] 
    SAMPLING_RATE = 33.0 
    CUTOFF_FREQ = 0.01
    
    print("Waiting for a sensor log file...")
    latest_csv = None
    while not latest_csv:
        latest_csv = get_latest_sensor_log()
        if not latest_csv:
            time.sleep(1)
            
    print(f"Found recent log file: {latest_csv}")
    
    tail_and_filter_csv(
        csv_path=latest_csv, 
        fs=SAMPLING_RATE, 
        cutoff_freq=CUTOFF_FREQ, 
        exclude_cols=COLUMNS_TO_IGNORE
    )
