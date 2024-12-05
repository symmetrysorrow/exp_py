import pandas as pd
import matplotlib.pyplot as plt

# ファイルの読み込み
file_path_0 = "F:/tagawa/data/20241203/room1_ch1ch2_220mK_920uA920uA_gain5_trig0.2V_rate500k_samples100k/CH0_pulse/output0.csv"  # output0のファイル名
file_path_1 = "F:/tagawa/data/20241203/room1_ch1ch2_220mK_920uA920uA_gain5_trig0.2V_rate500k_samples100k/CH1_pulse/output1.csv"  # output1のファイル名

# 各ファイルをDataFrameに読み込む
df0 = pd.read_csv(file_path_0)
df1 = pd.read_csv(file_path_1)

# "height" と "base" 列の確認と抽出
height_0 = df0["height"] if "height" in df0.columns else None
base_0 = df0["base"] if "base" in df0.columns else None
rise_0 = df0["rise"] if "base" in df0.columns else None

height_1 = df1["height"] if "height" in df1.columns else None
base_1 = df1["base"] if "base" in df1.columns else None
rise_1 = df1["rise"] if "base" in df0.columns else None

# "height - base" を計算
if base_0 is not None and base_1 is not None:
    height_base_0 = height_0 - base_0
    height_base_1 = height_1 - base_1
    
    # プロット
    plt.figure(figsize=(8, 8))
    plt.scatter(height_0, height_1, alpha=0.7)
    plt.title('Scatter Plot: (height) for output0 vs output1')
    plt.xlabel('output0 - (height0)')
    plt.ylabel('output1 - (height1)')
    plt.grid(True)
    plt.show()



else:
    print("いずれかのファイルに 'base' 列が存在しませんでした。")
