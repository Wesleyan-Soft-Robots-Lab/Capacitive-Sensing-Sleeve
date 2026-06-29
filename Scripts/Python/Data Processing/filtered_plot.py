import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import os

def load_sensor_data(csv_path, exclude_cols=None):
    if exclude_cols is None:
        exclude_cols = []
        
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: Could not find the file at {csv_path}")
        return None, None, None
    
    cols_to_keep = [col for col in df.columns if col not in exclude_cols]
    df_filtered = df[cols_to_keep]
    df_numeric = df_filtered.select_dtypes(include=[np.number])
    sensor_ids = df_numeric.columns.tolist()
    
    if not sensor_ids:
        raise ValueError("No numeric sensor columns found.")
        
    raw_data_2d = df_numeric.values
    return df, raw_data_2d, sensor_ids

def save_filtered_csv(df, filtered_data_2d, sensor_ids, exclude_cols, output_filename):
    df_output = pd.DataFrame(filtered_data_2d, columns=sensor_ids)
    
    if exclude_cols:
        for col in exclude_cols:
            if col in df.columns:
                df_output[col] = df[col]
                
    df_output = df_output[df.columns]
    
    # Save to CSV
    df_output.to_csv(output_filename, index=False)
    print(f"Saved: {os.path.basename(output_filename)}")

def plot_sensor_data(time_axis, raw_data_2d, filtered_datasets, sensor_ids, frequencies_to_plot, title='Raw vs. Filtered Sensor Data'):
    num_sensors = len(sensor_ids)
    fig, axes = plt.subplots(num_sensors, 1, figsize=(12, 2.5 * num_sensors), sharex=True)
    
    if num_sensors == 1:
        axes = [axes]
    
    cmap = plt.cm.YlGnBu
    colors = cmap(np.linspace(0.4, 1.0, max(1, len(frequencies_to_plot))))

    for i, sensor in enumerate(sensor_ids):
        axes[i].plot(time_axis, raw_data_2d[:, i], label='Raw Data', color="#e76f51", alpha=0.4, linewidth=1.5, zorder=1)
        
        for col, freq in enumerate(frequencies_to_plot):
            
            sensor_filtered = filtered_datasets[freq][:, i]
            
            lw = 3.0 - (col * 0.6) 
            z = 2 + col 
            
            label_text = freq if isinstance(freq, str) else f'{freq:.2f} Hz'
            axes[i].plot(
                time_axis, 
                sensor_filtered, 
                label=label_text, 
                color=colors[col], 
                linewidth=lw, 
                alpha=1.0, 
                zorder=z
            )
        
        axes[i].set_title(f'Sensor: {sensor}', loc='left', fontweight='bold')
        axes[i].set_ylabel('Raw Value')
        axes[i].legend(loc='upper right', fontsize='x-small', ncol=5)
        axes[i].grid(True, linestyle='--', alpha=0.4)

    axes[-1].set_xlabel('Time (seconds)', fontweight='bold', labelpad=10)
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    plt.tight_layout(pad=2.0, h_pad=2.5)
    fig.subplots_adjust(top=0.93)
    plt.show()

def plot_filtered_sensors(csv_path, fs, cutoff_freq, exclude_cols=None):
    df, raw_data_2d, sensor_ids = load_sensor_data(csv_path, exclude_cols)
    if df is None:
        return
        
    time_axis = np.arange(len(df)) / fs
    nyq = 0.5 * fs

    frequencies_to_plot = np.linspace(0.01, 2, 3)
    
    filtered_datasets = {}
    
    print("Filtering and saving data...")
    for freq in frequencies_to_plot:
        b, a = butter(4, freq / nyq, btype='low', analog=False)
        filtered_data_2d = filtfilt(b, a, raw_data_2d, axis=0)
        filtered_datasets[freq] = filtered_data_2d
        
        freq_label = f"{freq:.2f}Hz"
        output_filename = csv_path.replace('.csv', f'_FILTERED_{freq_label}.csv')
        
        save_filtered_csv(df, filtered_data_2d, sensor_ids, exclude_cols, output_filename)

    print("\nGenerating plots...")
    plot_sensor_data(time_axis, raw_data_2d, filtered_datasets, sensor_ids, frequencies_to_plot)

if __name__ == "__main__":
    
    MY_CSV_FILE = 'tests/data/cap-sensor_data/20260623/DEMO.csv'
    COLUMNS_TO_IGNORE = ['Timestamp'] 
    
    SAMPLING_RATE = 33.0 
    CUTOFF_FREQ = 2     
    
    plot_filtered_sensors(
        csv_path=MY_CSV_FILE, 
        fs=SAMPLING_RATE, 
        cutoff_freq=CUTOFF_FREQ, 
        exclude_cols=COLUMNS_TO_IGNORE
    )