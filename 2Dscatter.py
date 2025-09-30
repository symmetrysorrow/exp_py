import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from InquirerPy import inquirer
from matplotlib.widgets import RectangleSelector

folder = input("target folder: ")

df0 = pd.read_csv(folder + "/CH0_pulse/info.csv", header=0)
df1 = pd.read_csv(folder + "/CH1_pulse/info.csv", header=0)

common_ids = set(df0['key']) & set(df1['key'])

df0 = df0[df0['key'].isin(common_ids)].reset_index(drop=True)
df1 = df1[df1['key'].isin(common_ids)].reset_index(drop=True)

df0['key'] = df0['key'].astype(int)
df1['key'] = df1['key'].astype(int)

df0 = df0[df0['key'].isin(common_ids)].sort_values('key').reset_index(drop=True)
df1 = df1[df1['key'].isin(common_ids)].sort_values('key').reset_index(drop=True)


columns = ['PeakAverage', 'RiseTime', 'DecayTime']
channels = [0, 1]

# CLIで上下キーで選択
x_axis_ch = inquirer.select(
    message="X axis Channel:",
    choices=channels
).execute()
x_axis = inquirer.select(
    message="X axis Target:",
    choices=columns
).execute()

y_axis_ch = inquirer.select(
    message="Y axis Channel:",
    choices=channels
).execute()
y_axis = inquirer.select(
    message="Y axis Target:",
    choices=columns
).execute()

if x_axis_ch == 0:
    x_df = df0
else:
    x_df = df1

if y_axis_ch == 0:
    y_df = df0
else:
    y_df = df1

x_data = x_df[x_axis].values
y_data = y_df[y_axis].values

# 両方のデータのidも取得
x_ids = x_df['key'].values
y_ids = y_df['key'].values

fig, ax = plt.subplots()
sc = ax.scatter(x_data, y_data,s=5)

selected_ids = set()

def onselect(eclick, erelease):
    global selected_ids

    # 矩形の範囲を取得
    x_min, x_max = sorted([eclick.xdata, erelease.xdata])
    y_min, y_max = sorted([eclick.ydata, erelease.ydata])

    newly_selected = set()

    # 範囲内のデータを探す
    for i in range(len(x_data)):
        if x_min <= x_data[i] <= x_max and y_min <= y_data[i] <= y_max:
            newly_selected.add(x_ids[i])  # x_idsとy_idsは同じはず

    # 選択結果を更新
    selected_ids.update(newly_selected)

    # ファイルに保存
    with open(f"{folder}/selected_ids.txt", "w") as f:
        for id_val in sorted(selected_ids):
            f.write(f"{id_val}\n")
    print("Saved to selected_ids.txt")

    # 選択された点を別の色で scatter
    mask = np.isin(x_ids, list(newly_selected))
    ax.scatter(x_data[mask], y_data[mask], color='red', label='Selected')

    fig.canvas.draw()  # 描画更新

# RectangleSelectorを設定
toggle_selector = RectangleSelector(
    ax, onselect, useblit=True,
    button=[1],  # 左クリック
    minspanx=5, minspany=5, spancoords='pixels',
    interactive=True
)
print(f"min:{np.min(y_data)},max:{np.max(y_data)}")
plt.title("2D Scatter")
plt.ylim(np.min(y_data)*0.9,np.max(y_data)*1.1)
plt.show()
