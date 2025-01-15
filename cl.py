import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from sklearn.linear_model import RANSACRegressor
from scipy.optimize import curve_fit
from natsort import natsorted
import glob
import sys

def save_corrected_data(I_bias, V_out, y_fit, output_path):
    """補正後のデータを保存"""
    corrected_data = np.column_stack((I_bias, V_out, y_fit))
    header = "I_bias[uA], V_out[V] (original), V_out[V] (corrected)"
    np.savetxt(output_path, corrected_data, header=header, delimiter=",", fmt="%.6f")
    #print(f"Corrected data saved to {output_path}")

def CorrectJump(V_out,I_bias, idx_start, idx_stop, num_points_for_slope=10):
    """
    隣接するうちで最も差のある部分を探し、ジャンプを補正する。
    補正にはジャンプ前のデータの傾きを使う。
    """
    # 選択範囲のデータを取得
    V_out_range = V_out[idx_start:idx_stop]

    # 隣接する値の差分を計算
    diff = np.abs(np.diff(V_out_range))

    # 最も差が大きい位置（ジャンプ）のインデックスを特定
    jump_idx = np.argmax(diff)
    jump_idx = idx_start + jump_idx

    # 傾き計算: ジャンプ前の数点を使って傾きを推定
    slope_start_idx = jump_idx - num_points_for_slope  # 傾き計算に使う開始点
    if slope_start_idx < idx_start:
        slope_start_idx = idx_start  # 始点より前に行かないようにする

    x_points = I_bias[jump_idx-10:jump_idx].reshape(-1, 1)
    y_points = V_out[jump_idx-10:jump_idx]

    model = RANSACRegressor()
    model.fit(x_points, y_points)

    # 傾きと切片
    slope = model.estimator_.coef_[0]

    # 傾きに基づいて補正
    V_out[jump_idx+1:]+=(V_out[jump_idx]-V_out[jump_idx+1]+slope*(I_bias[jump_idx+1]-I_bias[jump_idx]))

    return V_out

def func(x, a, b):
    """フィッティング関数（例: 線形関数）"""
    return a * x + b

class RangeSelector:
    def __init__(self, I_bias, V_out):
        self.I_bias = I_bias
        self.V_out = V_out
        self.selected_range = (None, None)  # 選択した範囲のインデックス (start, stop)

    def on_select(self, eclick, erelease):
        """矩形選択の範囲取得"""
        x1, x2 = sorted((eclick.xdata, erelease.xdata))  # 範囲を昇順に整列
        self.selected_range = (
            np.searchsorted(self.I_bias, x1, side="left"),
            np.searchsorted(self.I_bias, x2, side="right")
        )
        print(f"Selected range: {self.I_bias[self.selected_range[0]]} to {self.I_bias[self.selected_range[1]-1]}")

    def select_range(self):
        """範囲を選択"""
        print("Drag to select a range on the plot.")
        fig, ax = plt.subplots()
        ax.plot(self.I_bias, self.V_out, marker="o", c="red", linewidth=1, markersize=6)
        ax.set_title("Select Range")
        ax.set_xlabel("I_bias[uA]")
        ax.set_ylabel("V_out[V]")
        ax.grid(True)

        # RectangleSelector を使用して範囲選択
        selector = RectangleSelector(
            ax,
            self.on_select,
            interactive=True,  # 矩形を動かせるようにする
            useblit=True,  # 描画の最適化
            button=[1],  # 左クリックで選択
            minspanx=0,  # 最小幅
            minspany=0,  # 最小高さ
            spancoords='data'  # データ座標系での選択
        )
        plt.show()

        return self.selected_range

def offset(data):

    data = data - data[0]

    if np.mean(data[:5]) < 0:
        data = data * -1
    return data

def main():
    path = input('path: ')
    os.chdir(path)
    temps = natsorted(glob.glob(f"*mK"))
    print(f"temps:{temps}")
    I_bias_array=[]
    V_out_array=[]
    for i,temp in enumerate(temps):
        if not os.path.exists('calibration'):
            os.mkdir('calibration')

        files = natsorted(glob.glob(f"{temp}/*.dat"))
        I_bias = []
        V_out = []
        for i in files:
            data = np.loadtxt(i)  # 適切なデータ読み取り関数に変更
            V_out.append(np.mean(data))
            I = os.path.splitext(os.path.basename(i))[0][10:-2]
            I_bias.append(int(I))

        I_bias = np.array(I_bias)
        V_out = np.array(V_out)  # オリジナルデータを保存
        V_out = offset(V_out)
        V_out_original=V_out.copy()
        # 一つ前の状態を保持
        V_out_previous = V_out.copy()
        selector = RangeSelector(I_bias, V_out)

        choice=0

        while True:
            # プロットを更新
            plt.figure(figsize=(10, 6))
            plt.plot(I_bias, V_out_original, marker="o", c="blue", linewidth=1, markersize=6, label="Original")
            if (V_out!=V_out_previous).any() and (V_out_original!=V_out_previous).any():
                plt.plot(I_bias, V_out_previous, marker="o", c="green", linewidth=1, markersize=6, label="Previous")
            if (V_out!=V_out_original).any() or choice==3:
                plt.plot(I_bias, V_out, marker="o", c="red", linewidth=1, markersize=6, label="Current")
            plt.title(f'{i}/{len(temps)} {temp}')
            plt.xlabel("I_bias[uA]")
            plt.ylabel("V_out[V]")
            plt.grid(True)
            plt.legend()
            plt.show()

            choice = int(input("[1]Single jump [2]Liner fit [3]Back [4]Help [0]Exit: "))

            if choice == 0:
                I_bias_array.append(I_bias)
                V_out_array.append(V_out)
                print("Finish")
                break
            elif choice in [1, 2]:
                V_out_previous = V_out.copy()
                # 矩形選択で範囲を取得
                idx_start, idx_stop = selector.select_range()
                
                if choice == 2:
                    # 線形フィット補正
                    try:
                        I_range = I_bias[idx_start:idx_stop]

                        # 線形フィット
                        popt, cov = curve_fit(func, I_bias[:5], V_out[:5])
                        corrected_values = func(I_range, *popt)

                        # 補正を適用
                        V_out[idx_start:idx_stop] = corrected_values
                    except Exception as e:
                        print(f"Error during linear fit: {e}")
                elif choice == 1:
                    V_out=CorrectJump(V_out,I_bias,idx_start,idx_stop)

            elif choice==3:
                V_pre=V_out_previous
                V_out_previous=V_out
                V_out=V_pre
                selector = RangeSelector(I_bias, V_out)

            elif choice==4:
                print("[1]Single Jump\n基本的にはこれを使っておけばOK。FlaxJumpが発生している場所を矩形で囲めば、最も大きくjumpしている部分をjumpより前の部分を参考にしながら補正する。FraxJumpが多発している部分で使うとうまく機能しない可能性あり。")
                print("[2]Liner fit\nフラックスジャンプが多発している場合、かつ超伝導(線形)に限り有効。選択範囲を全て線形に直す。常伝導(緩やかなカーブ)には使うと全てを線形にしてしまうので厳禁。")
                print("[3]Back\n一個前の状態に戻す。2個以上前には戻せないので注意。")
                print("[0]Exit\nこの温度での補正をやめて次の温度の補正に映る。最後の温度だったらデータを保存して終了する。")
                
            else:
                print("Invalid choice. Please select 0, 1, or 2.")

        data = np.column_stack((I_bias, V_out))
        np.savetxt(f"Calibration/{temp}.dat", data, header="I_bias, V_out", fmt='%f')

    for I_bias,V_out,temp in zip(I_bias_array,V_out_array,temps):
        plt.plot(I_bias,V_out,label=temp,marker="o")

    plt.xlabel("I_bias[uA]")
    plt.ylabel("V_out[V]")
    plt.grid(True)
    plt.legend()
    plt.savefig("rawdata/IV_calib_matome.png")
    plt.show()

if __name__ == "__main__":
    main()