import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

def plot_filtered_sensors(csv_path, fs, cutoff_freq, exclude_cols=None):
    if exclude_cols is None:
        exclude_cols = []
        
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: Could not find the file at {csv_path}")
        return
    
    cols_to_keep = [col for col in df.columns if col not in exclude_cols]
    df_filtered = df[cols_to_keep]
    df_numeric = df_filtered.select_dtypes(include=[np.number])
    sensor_ids = df_numeric.columns.tolist()
    
    if not sensor_ids:
        raise ValueError("No numeric sensor columns found.")
        
    raw_data_2d = df_numeric.values
    
    time_axis = np.arange(len(df)) / fs

    print(f"Applying order-4 Butterworth filter at {cutoff_freq} Hz...")
    nyq = 0.5 * fs
    normal_cutoff = cutoff_freq / nyq
    b, a = butter(4, normal_cutoff, btype='low', analog=False)
    
    filtered_data_2d = filtfilt(b, a, raw_data_2d, axis=0)

    num_sensors = len(sensor_ids)
    fig, axes = plt.subplots(num_sensors, 1, figsize=(12, 2.5 * num_sensors), sharex=True)
    
    if num_sensors == 1:
        axes = [axes]

    for i, sensor in enumerate(sensor_ids):
        axes[i].plot(time_axis, raw_data_2d[:, i], label='Raw Data', color='red', alpha=0.5, linewidth=1.5)
        
        axes[i].plot(time_axis, filtered_data_2d[:, i], label=f'Filtered ({cutoff_freq} Hz)', color='blue', linewidth=2)
        
        axes[i].set_title(f'Sensor: {sensor}', loc='left', fontweight='bold')
        axes[i].set_ylabel('Raw Value')
        axes[i].legend(loc='upper right')
        axes[i].grid(True, linestyle='--', alpha=0.6)

    axes[-1].set_xlabel('Time (seconds)', fontweight='bold', labelpad=10)
    
    fig.suptitle('Raw vs. Filtered Sensor Data', fontsize=16, fontweight='bold')
    
    plt.tight_layout(pad=2.0, h_pad=2.5)
    
    fig.subplots_adjust(top=0.93)
    
    plt.show()

if __name__ == "__main__":
    
    MY_CSV_FILE = '/Users/chris/Desktop/Capacitive-Sensing-Sleeve/tests/data/cap-sensor_data/20260623/DEMO.csv'
    COLUMNS_TO_IGNORE = ['Timestamp'] 
    
    SAMPLING_RATE = 33.0 
    CUTOFF_FREQ = 2     # The chosen elbow frequency
    
    plot_filtered_sensors(
        csv_path=MY_CSV_FILE, 
        fs=SAMPLING_RATE, 
        cutoff_freq=CUTOFF_FREQ, 
        exclude_cols=COLUMNS_TO_IGNORE
    )