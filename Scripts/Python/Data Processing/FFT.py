import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def normalizeData(csv_file):
    ds = pd.read_csv(csv_file)

    for col in ds.columns:
        if col != "Timestamp" and pd.api.types.is_numeric_dtype(ds[col]):
            baseline = ds[col].iloc[:1600].mean()
            ds[col] = ds[col] - baseline

    return ds


def transform(csv_file, sensor="8", cutoff=1):
    # Load and normalize data
   # ds = normalizeData(csv_file)
    ds = pd.read_csv(csv_file)

    time = ds["Timestamp"].to_numpy()
    signal = ds[sensor].to_numpy()

    # Sampling frequency
    dt = np.mean(np.diff(time))
    Fs = 1 / dt
    N = len(signal)

    # FFT
    fft_vals = np.fft.fft(signal)
    freqs = np.fft.fftfreq(N, dt)

    # Low-pass filter
    filtered_fft = fft_vals.copy()
    filtered_fft[np.abs(freqs) > cutoff] = 0

    # Reconstruct signal
    filtered_signal = np.real(np.fft.ifft(filtered_fft))

    # Noise estimate
    noise = signal - filtered_signal
    noise_peak = np.max(np.abs(noise))
    noise_rms = np.sqrt(np.mean(noise**2))
    noise_std = np.std(noise)

    print("Peak noise : ", noise_peak)
    print("noise Root Mean Square: ", noise_rms)
    print("noise Standard Deviation: ", noise_std)


    # Plot
    fig, ax = plt.subplots(3, 1, figsize=(14, 9), sharex=True)

    ax[0].plot(time, signal)
    ax[0].set_title("Original Sensor Measurement")
    ax[0].set_ylabel("Capacitance")

    ax[1].plot(time, filtered_signal)
    ax[1].set_title("Estimated Signal")
    ax[1].set_ylabel("Capacitance")

    ax[2].plot(time, noise)
    ax[2].set_title("Estimated Noise")
    ax[2].set_ylabel("Capacitance")
    ax[2].set_xlabel("Time (s)")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
        target_csv = "/Users/yordanos/Capacitive-Sensing-Sleeve/tests/data/cap-sensor_data/20260709/20260709_1_MOTOR_OFF_8_FDC_2cm_SensorLog.csv" 
        
        print(f"Loading and plotting data from {target_csv}...")
        try:
            transform(target_csv)
        
        except FileNotFoundError:
            print(f"Error: Could not find the file '{target_csv}'")
    