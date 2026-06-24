import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

def butter_lowpass_filter(data, cutoff_freq, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff_freq / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    
    filtered_data = filtfilt(b, a, data, axis=0)
    return filtered_data

def tune_filter_dynamic_sensors(csv_path, fs, min_freq, max_freq, steps=50, exclude_cols=None):
    if exclude_cols is None:
        exclude_cols = []
        
    df = pd.read_csv(csv_path)
    
    cols_to_keep = [col for col in df.columns if col not in exclude_cols]
    df_filtered = df[cols_to_keep]
    
    df_numeric = df_filtered.select_dtypes(include=[np.number])
    sensor_ids = df_numeric.columns.tolist()
    
    if not sensor_ids:
        raise ValueError("No numeric sensor columns found after exclusions.")
    
    raw_data_2d = df_numeric.values
    
    frequencies_to_test = np.linspace(min_freq, max_freq, steps)
    average_differences = []

    for freq in frequencies_to_test:
        try:
            filtered_data_2d = butter_lowpass_filter(raw_data_2d, freq, fs, order=4)
            
            difference = np.abs(raw_data_2d - filtered_data_2d)
            
            avg_diff = np.mean(difference)
            average_differences.append(avg_diff)
            
        except ValueError as e:
            print(f"Skipping frequency {freq:.2f}Hz: {e}")
            average_differences.append(np.nan)

    plt.figure(figsize=(10, 6))
    plt.plot(frequencies_to_test, average_differences, marker='o', linestyle='-', markersize=4)
    
    plt.title(f'Aggregate Filter Tuning (Across {len(sensor_ids)} Sensors)')
    plt.xlabel('Frequency Guess (Hz)')
    plt.ylabel('Global Average Absolute Difference')
    plt.grid(True, which='both', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    MY_CSV_FILE = '/Users/chris/Desktop/Capacitive-Sensing-Sleeve/tests/data/cap-sensor_data/20260623/DEMO.csv'
    
    COLUMNS_TO_IGNORE = ['Timestamp'] 
    SAMPLING_RATE = 33.0  
    
    START_FREQ = 0.5       
    END_FREQ = 15.0    
    
    try:
        tune_filter_dynamic_sensors(
            csv_path=MY_CSV_FILE, 
            fs=SAMPLING_RATE, 
            min_freq=START_FREQ, 
            max_freq=END_FREQ, 
            steps=80,
            exclude_cols=COLUMNS_TO_IGNORE 
        )
    except FileNotFoundError:
        print(f"Please update 'MY_CSV_FILE' to point to your actual file.")

