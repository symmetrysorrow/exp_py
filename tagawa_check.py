import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt

def loadbi(path, type):
    if type == "binary":
        with open(path, "rb") as fb:
            fb.seek(4)
            data = np.frombuffer(fb.read(), dtype="float64")
    elif type == "text":
        data = np.loadtxt(path)
    return data

def apply_lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyquist  # Normalized cutoff frequency
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data

def process_and_plot(file_path1, file_path2, fs, cutoff, n_samples):
    # Load binary data
    data1 = loadbi(file_path1, "binary")
    data2 = loadbi(file_path2, "binary")

    # Compute baselines
    baseline1 = np.mean(data1[:500])
    baseline2 = np.mean(data2[:500])

    # Correct data by subtracting baselines
    corrected_data1 = data1 - baseline1
    corrected_data2 = data2 - baseline2

    # Apply low-pass filter
    filtered_data1 = apply_lowpass_filter(corrected_data1, cutoff, fs)
    filtered_data2 = apply_lowpass_filter(corrected_data2, cutoff, fs)

    # Create time axis
    time = np.linspace(0, (n_samples - 1) / fs, n_samples)

    # Plotting the corrected and filtered data
    plt.figure(figsize=(12, 6))
    #plt.plot(time, corrected_data1[:n_samples], label='Corrected Data CH1', linewidth=0.8, color='orange', alpha=0.5)
    plt.scatter(time, filtered_data1[:n_samples], label='Filtered Data CH1 (10kHz LPF)', linewidth=0.8, color='blue', s=0.1)
    #plt.plot(time, corrected_data2[:n_samples], label='Corrected Data CH2', linewidth=0.8, color='green', alpha=0.5)
    plt.scatter(time, filtered_data2[:n_samples], label='Filtered Data CH2 (10kHz LPF)', linewidth=0.8, color='red', s=0.1)
    plt.title('event 95397')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude (µA)')
    plt.legend()
    plt.grid()
    plt.show()

# File paths for two pulse data files
file_path_ch1 = "G:/tagawa/20250116/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10/CH0_pulse/rawdata/CH0_95397.dat"
file_path_ch2 = "G:/tagawa/20250116/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10/CH1_pulse/rawdata/CH1_95397.dat"

# Parameters
fs = 500e3  # Sampling rate (500 kHz)
cutoff = 10e3  # Low-pass filter cutoff frequency (10 kHz)
n_samples = 100000  # Number of samples to process

# Process and plot the data
process_and_plot(file_path_ch1, file_path_ch2, fs, cutoff, n_samples)
