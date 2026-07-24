import numpy as np
import pandas as pd
from scipy.stats import iqr
import matplotlib.pyplot as plt


def normalizeData(csv_file):
    ds = pd.read_csv(csv_file)

    averages = {}
    max_vals = {}
    min_vals = {}

    max_y = 0
    min_y = 0

    for col in ds.columns:
        if col != "Timestamp":
            if pd.api.types.is_numeric_dtype(ds[col]):
                averages[col] = ds[col].iloc[:1600].mean()
                ds[col] = ds[col] - averages[col]

                max_vals[col] = ds[col].abs().max()
                min_vals[col] = ds[col].min()

                max_y = max(max_y, max_vals[col])
                min_y = min(min_y, min_vals[col])

    return ds, max_y, min_y


def transform(csv_file, sensor="0", cutoff=0.001): 
    # Load and normalize data
    ds, maxy, miny = normalizeData(csv_file)

    # Extract time and sensor signal
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

    print("Peak noise:", noise_peak)
    print("Noise Root Mean Square:", noise_rms)
    print("Noise Standard Deviation:", noise_std)
    print("IQR:", iqr(noise))
    print("min_y:", miny)
    print("max_y:", maxy)

    # Plot
    fig, ax = plt.subplots(3, 1, figsize=(14, 9), sharex=True)

    # Original signal
    ax[0].plot(time, signal)
    ax[0].set_title("Original Sensor Measurement")
    ax[0].set_ylabel("Capacitance")
    ax[0].set_xlabel("Time (s)")
    ax[0].set_ylim(1.05 * miny, 1.05 * maxy)
    ax[0].locator_params(axis="x", nbins=15)

    # Estimated signal
    ax[1].plot(time, filtered_signal)
    ax[1].set_title("Estimated Signal")
    ax[1].set_ylabel("Capacitance")
    ax[1].set_xlabel("Time (s)")
    ax[1].set_ylim(1.05 * miny, 1.05 * maxy)
    ax[1].locator_params(axis="x", nbins=15)
    # Estimated noise
    ax[2].plot(time, noise)
    ax[2].set_title("Estimated Noise")
    ax[2].set_ylabel("Capacitance")
    ax[2].set_xlabel("Time (s)")
    ax[2].set_ylim(1.05 * miny, 1.05 * maxy)
    ax[2].locator_params(axis="x", nbins=15)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    target_csv = "tests/data/cap-sensor_data/20260715/20260715_1_ACT+SYM.csv"

    print(f"Loading and plotting data from {target_csv}...")

    try:
        transform(target_csv)
    except FileNotFoundError:
        print(f"Error: Could not find the file '{target_csv}'")