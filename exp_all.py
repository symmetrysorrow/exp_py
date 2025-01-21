#2024/12/04 Hata&tagawa

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from scipy import signal
import shutil
from natsort import natsorted
import json
import pprint
import sys
import re
import matplotlib.cm as cm
import tqdm

Data_path = "G:/tagawa/20250116/room1ch2ch3_180mK_800uA800uA_difftrig1E-5_rate500k_samples100k_gain10"


def ReadPulse(pulse,path):
    with open(f"{Data_path}/setting.json") as f:
        jsn = json.load(f)
    try:
        ws = jsn["main"]["cutoff"] / jsn["Config"]["rate"] * 2
        b, a = signal.bessel(2, ws, "low")

        base = np.mean(pulse[jsn["Config"]["presamples"] - jsn["main"]["base_x"] : jsn["Config"]["presamples"] - jsn["main"]["base_x"] + jsn["main"]["base_w"]])
        pulse=pulse-base

        try:

            if jsn["main"]["cutoff"]>0:
                pulse = signal.filtfilt(b, a, pulse)
        except:
            print("filt err")

        peak = np.max(pulse[jsn["Config"]["presamples"] : jsn["Config"]["presamples"] + jsn["main"]["peak_max"]])
        peak_index = np.argmax(pulse[jsn["Config"]["presamples"] : jsn["Config"]["presamples"] + jsn["main"]["peak_max"]]) + jsn["Config"]["presamples"]
        peak_av = np.mean(pulse[peak_index - jsn["main"]["peak_x"] : peak_index - jsn["main"]["peak_x"] + jsn["main"]["peak_w"]])

        for i in reversed(range(0, peak_index)):
            if pulse[i] <= peak * jsn["main"]["rise_high"]:
                rise_high = i
                break

        try:
            rise_high+=0
        except:
            rise_high=0
        for j in reversed(range(0, rise_high)):
            if pulse[j] <= peak * jsn["main"]["rise_low"]:
                rise_low = j
                break

        try:
            rise_low+=0
        except:
            rise_low=0

        rise = (rise_high - rise_low) / jsn["Config"]["rate"]

        for i in range(peak_index, len(pulse)):
            if pulse[i] <= peak * jsn["main"]["decay_high"]:
                decay_high = i
                break
        try:
            decay_high+=0
        except:
            decay_high=0
        for j in range(decay_high, len(pulse)):
            if pulse[j] <= peak * jsn["main"]["decay_low"]:
                decay_low = j
                break

        try:
            decay_low+=0
        except:
            decay_low=0

        decay = (decay_low - decay_high) / jsn["Config"]["rate"]

        area=np.sum(pulse[peak_index - jsn["main"]["area_x"] : peak_index - jsn["main"]["area_x"] + jsn["main"]["area_w"]])

        return [base,peak_av,peak_index,rise,decay,area]
    except:
        print(path)
        return [0,0,0,0,0,0]

def checkPulse():
    Channels = []

    pattern = re.compile(r'CH(\d+)_pulse')
    for folder_name in os.listdir(Data_path):
        match = pattern.match(folder_name)
        if match:
            Channels.append(int(match.group(1)))
    ch=input(f"Which Channel? {Channels}:")
    try:
        ch = int(ch)  # int型への変換を試す
        if ch not in Channels:
            raise ValueError(f"{ch} is not in the Channels")
            sys.exit()
    except ValueError:
        print("Input error")
        sys.exit()

    pulse_pathes = natsorted(glob.glob(f'{Data_path}/CH{ch}_pulse/rawdata/CH{ch}_*.dat'))
    max=len(pulse_pathes)

    num=input(f"which pulse? 1~{max}:")
    
    try:
        num = int(num)  # int型への変換を試す
        if num <0 or num>max:
            raise ValueError(f"{num} is invalid")
            sys.exit()
    except ValueError:
        print("Input error")
        sys.exit()

    path=f"{Data_path}/CH{ch}_pulse/rawdata/CH{ch}_{num}.dat"

    with open(path,"rb") as fb:
        fb.seek(4)
        pulse = np.frombuffer(fb.read(), dtype="float64")

    with open(f"{Data_path}/setting.json") as f:
        jsn = json.load(f)

    time=np.arange(0,1/jsn["Config"]["rate"]*jsn["Config"]["samples"],1/jsn["Config"]["rate"])

    plt.plot(time,pulse)
    plt.show()
    
    result=ReadPulse(pulse,path)

    pulse=pulse-result[0]
    plt.plot(time,pulse,label="Normal",color="blue")

    ws = jsn["main"]["cutoff"] / jsn["Config"]["rate"] * 2
    b, a = signal.bessel(2, ws, "low")

    

    if jsn["main"]["cutoff"]>0:
        pulse = signal.filtfilt(b, a, pulse)
        plt.plot(time,pulse,label="Bessel",color="red")

    peak = np.max(pulse[jsn["Config"]["presamples"] : jsn["Config"]["presamples"] + jsn["main"]["peak_max"]])

    for i in reversed(range(0, result[2])):
        if pulse[i] <= peak * jsn["main"]["rise_high"]:
            rise_high = i
            break

    try:
        rise_high+=0
    except:
        rise_high=0
    for j in reversed(range(0, rise_high)):
        if pulse[j] <= peak * jsn["main"]["rise_low"]:
            rise_low = j
            break
    try:
        rise_low+=0
    except:
        rise_low=0

    for i in range(result[2], len(pulse)):
        if pulse[i] <= peak * jsn["main"]["decay_high"]:
            decay_high = i
            break
    try:
        decay_high+=0
    except:
        decay_high=0
    for j in range(decay_high, len(pulse)):
        if pulse[j] <= peak * jsn["main"]["decay_low"]:
            decay_low = j
            break

    try:
        decay_low+=0
    except:
        decay_low=0

    plt.axvline(x=time[jsn["Config"]["presamples"]],label="presamples",color="gray",linestyle="--")
    plt.axvline(x=time[(jsn["Config"]["presamples"] + jsn["main"]["peak_max"])],label="peak end",color="black",linestyle="--")
    plt.axvline(x=time[rise_low],label="rise_low",color="red",linestyle="--")
    plt.axvline(x=time[rise_high],label="rise_high",color="orange",linestyle="--")
    plt.axvline(x=time[decay_low],label="decay_low",color="blue",linestyle="--")
    plt.axvline(x=time[decay_high],label="decay_high",color="green",linestyle="--")

    plt.plot(result[2]/jsn["Config"]["rate"],result[1],marker="o",markersize=10,label="peak_av")
    plt.scatter(time[result[2]],pulse[result[2]],label="peak")
    plt.legend()
    plt.grid()
    plt.xlabel("Time[s]")
    plt.ylabel("amplitude[V]")
    plt.show()


def NormalOutput():
    print("normal")
    with open(f"{Data_path}/setting.json") as f:
        jsn = json.load(f)
    pattern = re.compile(r'CH(\d+)_pulse')
    Channels = []
    for folder_name in os.listdir(Data_path):
        match = pattern.match(folder_name)
        if match:
            Channels.append(int(match.group(1)))
    cnt=1
    for ch in Channels:
        print(f"{cnt}/{len(Channels)}")
        cnt+=1
        pulse_pathes = natsorted(glob.glob(f'{Data_path}/CH{ch}_pulse/rawdata/CH{ch}_*.dat'))
        results=[]
        pulse_numbers=[]
        #pulse_pathes=list(reversed(pulse_pathes))
        for path in tqdm.tqdm(pulse_pathes):
            pattern = fr'CH{ch}_(\d+).dat'
            match = re.search(pattern, path)
            pulse_numbers.append(match.group(1))
            with open(path, "rb") as fb:
                fb.seek(4)
                data = np.frombuffer(fb.read(), dtype="float64")
                results.append(ReadPulse(data,path))

        columns=["base","height","peak_index","rise","decay","area"]
        df = pd.DataFrame(results,columns=columns,index=pulse_numbers)
        df.to_csv(f"{Data_path}/CH{ch}_pulse/output.csv")    

NormalOutput()
#checkPulse()