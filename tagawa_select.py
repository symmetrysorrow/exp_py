import pandas as pd
import matplotlib.pyplot as plt

# ファイルの読み込み
file_path_0 = "F:/tagawa/20250117/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10/CH0_pulse/output.csv"  # output0のファイル名
file_path_1 = "F:/tagawa/20250117/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10/CH1_pulse/output.csv"    # output1のファイル名

# 各ファイルをDataFrameに読み込む
df0 = pd.read_csv(file_path_0)
df1 = pd.read_csv(file_path_1)

# "height" と "base" 列の確認と抽出
height_0 = df0["height"] if "height" in df0.columns else None
base_0 = df0["base"] if "base" in df0.columns else None
rise_0 = df0["rise"] if "base" in df0.columns else None
decay_0 = df0["decay"] if "base" in df0.columns else None
area_0 = df0["area"] if "area" in df0.columns else None

height_1 = df1["height"] if "height" in df1.columns else None
base_1 = df1["base"] if "base" in df1.columns else None
rise_1 = df1["rise"] if "base" in df0.columns else None
decay_1 = df1["decay"] if "base" in df0.columns else None
area_1 = df1["area"] if "area" in df0.columns else None

# height
if base_0 is not None and base_1 is not None:
    
    # プロット
    plt.figure(figsize=(8, 8))
    plt.scatter(height_0, height_1, alpha=0.7 ,s=1)
    plt.title('CH1_height vs CH2_height')
    #plt.xlim(-0.01,0.2)
    #plt.ylim(-0.01,0.175)
    plt.xlabel('CH1_height')
    plt.ylabel('CH2_height')
    plt.grid(True)
    plt.show()

    """""""""
    plt.figure(figsize=(8, 8))
    plt.scatter(rise_0, height_0, alpha=0.7 ,s=5)
    plt.title('CH1_rise time vs CH1_pulse height')
    plt.xlabel('CH1_rise time')
    plt.ylabel('CH1_pulse height')
    #plt.xlim(-0.005,0.25)
    #plt.ylim(-0.005,0.25)
    plt.grid(True)
    plt.show()
    
    plt.figure(figsize=(8, 8))
    plt.scatter(rise_1, height_1, alpha=0.7 ,s=5)
    plt.title('CH2_rise time vs CH2_pulse height')
    plt.xlabel('CH2_rise time')
    plt.ylabel('CH2_pulse height')
    #plt.xlim(-0.005,0.25)
    #plt.ylim(-0.005,0.25)
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(8, 8))
    plt.scatter(decay_0, height_0, alpha=0.7 ,s=5)
    plt.title('CH1_decay time vs CH1_pulse height')
    plt.xlabel('CH1_decay time')
    plt.ylabel('CH1_pulse height')
    #plt.xlim(-0.005,0.25)
    #plt.ylim(-0.005,0.25)
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(8, 8))
    plt.scatter(decay_1, height_1, alpha=0.7 ,s=5)
    plt.title('CH2_decay time vs CH2_pulse height')
    plt.xlabel('CH2_decay time')
    plt.ylabel('CH2_pulse height')
    #plt.xlim(-0.005,0.25)
    #plt.ylim(-0.005,0.25)
    plt.grid(True)
    plt.show()
    """""




else:
    print("いずれかのファイルに 'base' 列が存在しませんでした。")
