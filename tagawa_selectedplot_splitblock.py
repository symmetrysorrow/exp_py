import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ファイルパス設定
file_path_0 = "G:/tagawa/20250116/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10/CH0_pulse/output.csv"
file_path_1 = "G:/tagawa/20250116/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10/CH1_pulse/output.csv"

# selected_index.txt のパス
selected_index_path_0 = os.path.join(os.path.dirname(file_path_0), "G:/tagawa/20250116/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10/CH0_pulse/selected_index_0.txt")
selected_index_path_1 = os.path.join(os.path.dirname(file_path_1), "G:/tagawa/20250116/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10/CH1_pulse/selected_index_1.txt")

# CSVファイルの読み込み
df0 = pd.read_csv(file_path_0)
df1 = pd.read_csv(file_path_1)

# プロットする列名（データに合わせて変更）
x_col_0 = 'height'
y_col_1 = 'height'

# インデックス列の設定
index_col_0 = 'Unnamed: 0'
index_col_1 = 'Unnamed: 0'

# 選択されたインデックスを読み込む
if not os.path.exists(selected_index_path_0) or not os.path.exists(selected_index_path_1):
    raise FileNotFoundError("selected_index.txt ファイルが見つかりません。")

with open(selected_index_path_0, 'r') as f:
    selected_indices_0 = [int(line.strip()) for line in f.readlines()]

with open(selected_index_path_1, 'r') as f:
    selected_indices_1 = [int(line.strip()) for line in f.readlines()]

# 選択されたインデックスのデータをフィルタリング
filtered_df0 = df0[df0[index_col_0].isin(selected_indices_0)]
filtered_df1 = df1[df1[index_col_1].isin(selected_indices_1)]

# データを結合
filtered_data = pd.DataFrame({
    'height_ch0': filtered_df0[x_col_0].values,
    'height_ch1': filtered_df1[y_col_1].values,
    'index_0': filtered_df0[index_col_0].values,
    'index_1': filtered_df1[index_col_1].values
})

# データを \(y = ax\) に基づいてスコアリング
x = filtered_data['height_ch0'].values
y = filtered_data['height_ch1'].values

# スコアとして \(y / x\) を計算しソート
scores = y / x
sorted_indices = np.argsort(scores)
sorted_data = filtered_data.iloc[sorted_indices]

# データを均等に11分割
n_regions = 11
region_size = len(sorted_data) // n_regions
regions = []

for i in range(n_regions):
    start_idx = i * region_size
    if i == n_regions - 1:
        # 最後の領域に残りを含める
        end_idx = len(sorted_data)
    else:
        end_idx = (i + 1) * region_size
    regions.append(sorted_data.iloc[start_idx:end_idx])

# 傾きの計算 (境界となる直線の傾き)
boundary_slopes = []
for region in regions[:-1]:  # 最後の境界は不要
    boundary_slopes.append(region['height_ch1'].iloc[-1] / region['height_ch0'].iloc[-1])

# 結果を保存
output_dir = os.path.dirname(file_path_0)  # 保存ディレクトリ
for i, region in enumerate(regions):
    output_file = os.path.join(output_dir, f"region_{i + 1}_index.txt")
    region[['index_0', 'index_1']].to_csv(output_file, index=False, header=False)
    print(f"Region {i + 1}: {len(region)} points saved to {output_file}")

# プロット
fig, ax = plt.subplots(figsize=(8, 8))
colors = plt.cm.viridis(np.linspace(0, 1, n_regions))

for i, region in enumerate(regions):
    ax.scatter(region['height_ch0'], region['height_ch1'], s=10, color=colors[i], label=f"Region {i + 1}")

# 分割線を描画
x_vals = np.linspace(0, filtered_data['height_ch0'].max(), 100)  # x=0から始める
for slope in boundary_slopes:
    ax.plot(x_vals, slope * x_vals, '--', color='gray', alpha=0.7)  # 原点から引く

ax.set_xlabel('CH1_height')
ax.set_ylabel('CH2_height')
#ax.set_title('Pulse Data Divided into 11 Equal Regions using y=ax (from origin)')
ax.legend([f"block {i + 1}" for i in range(n_regions)])
plt.show()
