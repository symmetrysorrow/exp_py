# 2022/09/12
# それぞれのデータの周波数スペクトルの平均（モデルノイズ）を出力


import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack as fft
import os
from natsort import natsorted
import glob
import shutil
import getpara as gp
import pandas as pd
import json
import tqdm


# 実行
def main():
    set = gp.loadJson()
    if not "eta" in set["Config"]:
        eta = input("eta: ")
        set["Config"]["eta"] = float(eta)
        jsn = json.dumps(set, indent=4)
        with open("setting.json", "w") as file:
            file.write(jsn)
    os.chdir(set["Config"]["path"])
    ch = set["Config"]["channel"]
    rate, samples = set["Config"]["rate"], set["Config"]["samples"]
    eta = set["Config"]["eta"] * 1e-6
    time = gp.data_time(rate, samples)
    fq = np.arange(0, rate, rate / samples)
    output = f'CH{set["Config"]["channel"]}_noise/output/{set["Config"]["output"]}'

    model = np.array(0) * samples
    noise = natsorted(glob.glob(f"CH{ch}_noise/rawdata/CH{ch}_*.dat"))

    for i in tqdm.tqdm(noise):
        try:
            data = gp.loadbi(i, "binary")
            base, data_ba = gp.baseline(data, set["Config"]["presamples"], 1000, 500)
            if set["main"]["cutoff"] > 0:
                data = gp.BesselFilter(data, rate, set["main"]["cutoff"])
            peak = np.max(data_ba)
            if (base <= -3 and base >= 3) or peak >= float(set["Config"]["threshold"]):
                print("error")
                continue
            else:
                data_fft = np.fft.fft(data)
            amp = np.abs(data_fft)
            model = model + amp

        except FileNotFoundError:
            continue
    
    model = model / len(noise)
    df = rate / samples
    power = model**2 / df
    amp_dens = np.sqrt(power)
    amp_dens = amp_dens * eta * 1e+6
    print(amp_dens)
    np.savetxt(f"{output}/modelnoise.txt", amp_dens)

    # スペクトルをグラフ化
    plt.plot(fq[: int(samples / 2) + 1], amp_dens[: int(samples / 2) + 1]*1e-12, linestyle="-", linewidth=0.7)
    plt.loglog()
    plt.xlabel("Frequency[Hz]")
    plt.ylabel("Intensity[A/Hz$^{1/2}$]")
    plt.grid()
    plt.savefig(f"{output}/modelnoise.png")
    plt.show()


if __name__ == "__main__":
    main()
