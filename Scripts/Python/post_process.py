import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

def butter_lowpass_filter(data, cutoff_freq, fs, order=4):
    """
    Designs and applies an order-4 lowpass Butterworth filter.
    Handles both 1D arrays (single sensor) and 2D arrays (multiple sensors).
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff_freq / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    
    # axis=0 ensures the filter applies vertically down each column independently
    filtered_data = filtfilt(b, a, data, axis=0)
    return filtered_data

def tune_filter_dynamic_sensors(csv_path, fs, min_freq, max_freq, steps=50, exclude_cols=None):
    """
    Dynamically detects sensor columns and finds the optimal filter frequency 
    by averaging the heuristic across all sensors simultaneously.
    """
    if exclude_cols is None:
        exclude_cols = []
        
    # 1. Load the data
    df = pd.read_csv(csv_path)
    
    # 2. Dynamically filter out non-sensor columns
    # Drop explicitly excluded columns (e.g., Time, Date, Index)
    cols_to_keep = [col for col in df.columns if col not in exclude_cols]
    df_filtered = df[cols_to_keep]
    
    # Isolate only numeric columns (ignores any stray string/metadata columns)
    df_numeric = df_filtered.select_dtypes(include=[np.number])
    sensor_ids = df_numeric.columns.tolist()
    
    if not sensor_ids:
        raise ValueError("No numeric sensor columns found after exclusions.")
        
    print(f"Dynamically detected {len(sensor_ids)} sensor columns.")
    if len(sensor_ids) > 5:
        print(f"First few sensors: {sensor_ids[:5]}...")
    else:
        print(f"Sensors: {sensor_ids}")
    
    # Convert all sensor data to a single 2D numpy array for fast processing
    raw_data_2d = df_numeric.values
    
    # 3. Generate progressively higher frequency values
    frequencies_to_test = np.linspace(min_freq, max_freq, steps)
    average_differences = []
    
    print(f"Testing {steps} frequencies from {min_freq}Hz to {max_freq}Hz across all sensors...")

    # 4. Run the heuristic across the entire 2D matrix
    for freq in frequencies_to_test:
        try:
            # Filter all columns simultaneously
            filtered_data_2d = butter_lowpass_filter(raw_data_2d, freq, fs, order=4)
            
            # Find the absolute difference matrix
            difference = np.abs(raw_data_2d - filtered_data_2d)
            
            # Take the grand mean of the difference across ALL sensors and ALL timepoints
            avg_diff = np.mean(difference)
            average_differences.append(avg_diff)
            
        except ValueError as e:
            print(f"Skipping frequency {freq:.2f}Hz: {e}")
            average_differences.append(np.nan)

    # 5. Plot the master aggregate elbow
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
    
    # Add any columns here that are NOT sensor data (like timestamps or IDs)
    # The script will automatically grab everything else.
    COLUMNS_TO_IGNORE = ['Timestamp'] 
    
    SAMPLING_RATE = 100.0  
    START_FREQ = 0.1       
    END_FREQ = 20.0        
    
    try:
        tune_filter_dynamic_sensors(
            csv_path=MY_CSV_FILE, 
            fs=SAMPLING_RATE, 
            min_freq=START_FREQ, 
            max_freq=END_FREQ, 
            steps=60,
            exclude_cols=COLUMNS_TO_IGNORE 
        )
    except FileNotFoundError:
        print(f"Please update 'MY_CSV_FILE' to point to your actual file.")