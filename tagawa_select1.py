import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.widgets import PolygonSelector
from matplotlib.path import Path

# 2つのファイルパス
file_path_0 = "G:/tagawa/20250116/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10/CH0_pulse/output.csv"  # 1つ目のCSVファイル
file_path_1 = "G:/tagawa/20250116/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10/CH1_pulse/output.csv" # 2つ目のCSVファイル

# CSVファイルの読み込み
df0 = pd.read_csv(file_path_0)
df1 = pd.read_csv(file_path_1)

# プロットする列名（データに合わせて変更）
x_col_0 = 'height'
y_col_1 = 'height'

# インデックス列の設定
index_col_0 = 'Unnamed: 0'
index_col_1 = 'Unnamed: 0'

# データの確認
if x_col_0 not in df0.columns:
    raise ValueError(f"1つ目のファイルに '{x_col_0}' 列が存在しません。")
if y_col_1 not in df1.columns:
    raise ValueError(f"2つ目のファイルに '{y_col_1}' 列が存在しません。")
if index_col_0 not in df0.columns or index_col_1 not in df1.columns:
    raise ValueError("指定したインデックス列が存在しません。")

# データを結合して1つのプロットに統合
merged_data = pd.DataFrame({
    'height_ch0': df0[x_col_0],
    'height_ch1': df1[y_col_1],
    'index_0': df0[index_col_0],
    'index_1': df1[index_col_1]
})

# コールバック関数
def onselect(verts):
    path = Path(verts)
    points = merged_data[['height_ch0', 'height_ch1']].values
    contained = path.contains_points(points)
    selected_data = merged_data[contained]
    
    # 選択されたインデックスを抽出
    selected_indices_0 = selected_data['index_0'].tolist()
    selected_indices_1 = selected_data['index_1'].tolist()
    
    # 保存先のディレクトリを取得
    dir_path_0 = os.path.dirname(file_path_0)
    dir_path_1 = os.path.dirname(file_path_1)
    
    # 保存ファイルパスを生成
    output_file_0 = os.path.join(dir_path_0, "selected_index_0.txt")
    output_file_1 = os.path.join(dir_path_1, "selected_index_1.txt")
    
    # ファイルに保存
    with open(output_file_0, 'w') as f:
        f.write("\n".join(map(str, selected_indices_0)))
    with open(output_file_1, 'w') as f:
        f.write("\n".join(map(str, selected_indices_1)))
    
    # 結果を表示
    print(f"Selected indexes saved to {output_file_0} and {output_file_1}:")
    print("File 0 Indices:", selected_indices_0)
    print("File 1 Indices:", selected_indices_1)

# グラフを描画
fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(merged_data['height_ch0'], merged_data['height_ch1'], alpha=0.5, s=5)
ax.set_xlim(-0.005, 0.08)
ax.set_ylim(-0.005, 0.10)
ax.set_xlabel('Height CH0')
ax.set_ylabel('Height CH1')

# PolygonSelector を設定
selector = PolygonSelector(ax, onselect, useblit=True)

# 描画を表示
plt.show()

# セレクタを有効にする
selector.set_active(True)
