import os
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

def calculate_average_pulse(index_file_path, base_dir, fs, cutoff, n_samples, channel):
    # インデックス番号を読み込む（1列目のみ、カンマ区切りに対応）
    indices = np.loadtxt(index_file_path, delimiter=',', usecols=0, dtype=int)
    
    # 平均パルスを格納するリスト
    pulse_list = []
    
    for index in indices:
        # 指定チャンネルのパルスデータのパスを生成
        file_path = os.path.join(base_dir, f"rawdata/{channel}_{index}.dat")
        
        # データを読み込む
        data = loadbi(file_path, "binary")
        
        # ベースライン補正
        baseline = np.mean(data[:500])
        corrected_data = data - baseline
        
        # ローパスフィルタ適用
        filtered_data = apply_lowpass_filter(corrected_data, cutoff, fs)
        
        # 必要なサンプル数に切り取ってリストに追加
        pulse_list.append(filtered_data[:n_samples])
    
    # 全体の平均パルスを計算して返す
    return np.mean(pulse_list, axis=0)

# パラメータ
fs = 500e3  # サンプリングレート (500 kHz)
cutoff = 10e3  # ローパスフィルタのカットオフ周波数 (10 kHz)
n_samples = 100000  # 処理するサンプル数

# CH0の平均パルスを計算
index_file_path_ch0 = "G:/tagawa/20250116/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10/CH0_pulse/region_2_index.txt"
base_dir_ch0 = "G:/tagawa/20250116/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10/CH0_pulse"
average_pulse_ch0 = calculate_average_pulse(index_file_path_ch0, base_dir_ch0, fs, cutoff, n_samples, "CH0")

# CH1の平均パルスを計算
index_file_path_ch1 = index_file_path_ch0
base_dir_ch1 = "G:/tagawa/20250116/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10/CH1_pulse"
average_pulse_ch1 = calculate_average_pulse(index_file_path_ch1, base_dir_ch1, fs, cutoff, n_samples, "CH1")

# 時間軸を生成
time = np.linspace(0, (n_samples - 1) / fs, n_samples)

# 平均パルスを重ねてプロット
plt.figure(figsize=(12, 6))
plt.plot(time, average_pulse_ch0, label='Average Pulse (CH0)', linewidth=1.2, color='blue')
plt.plot(time, average_pulse_ch1, label='Average Pulse (CH1)', linewidth=1.2, color='red')
plt.title('Average Pulse for CH0 and CH1')
plt.xlabel('Time (seconds)')
plt.ylabel('Amplitude (µA)')
plt.legend()
plt.grid()
plt.show()
