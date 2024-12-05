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

Data_path="E:/tagawa/20241203/room1_ch1ch2_220mK_920uA920uA_gain5_trig0.2V_rate500k_samples100k"


def ReadPulse(pulses):
    with open(f"{Data_path}/setting.json") as f:
        jsn = json.load(f)

    Result_data=[]

    ws = jsn["Config"]["samples"] / jsn["Config"]["rate"] * 2
    b, a = signal.bessel(2, ws, "low")

    for pulse in pulses:
        base = np.mean(pulse[jsn["Config"]["presamples"] - jsn["main"]["base_x"] : jsn["Config"]["presamples"] - jsn["main"]["base_x"] + jsn["main"]["base_w"]])
        pulse=pulse-base

        if jsn["main"]["cutoff"]>0:
            pulse = signal.filtfilt(b, a, pulse)

        peak = np.max(pulse[jsn["Config"]["presamples"] : jsn["Config"]["presamples"] + jsn["main"]["peak_max"]])
        peak_index = np.argmax(pulse[jsn["Config"]["presamples"] : jsn["Config"]["presamples"] + jsn["main"]["peak_max"]]) + jsn["Config"]["presamples"]
        peak_av = np.mean(pulse[peak_index - jsn["main"]["peak_x"] : peak_index - jsn["main"]["peak_x"] + jsn["main"]["peak_w"]])

        for i in reversed(range(0, peak_index)):
            if pulse[i] <= peak * jsn["main"]["rise_high"]:
                rise_90 = i
                break
        for j in reversed(range(0, rise_90)):
            if pulse[j] <= peak * jsn["main"]["rise_low"]:
                rise_10 = j
                break

        rise = (rise_90 - rise_10) / jsn["Config"]["rate"]

        for i in range(peak_index, len(pulse)):
            if pulse[i] <= peak * jsn["main"]["decay_high"]:
                decay_90 = i
                break
        for j in range(decay_90, len(pulse)):
            if pulse[j] <= peak * jsn["main"]["decay_low"]:
                decay_10 = j
                break

        decay = (decay_10 - decay_90) / jsn["Config"]["rate"]

        area=np.sum(pulse[peak_index - jsn["main"]["area_x"] : peak_index - jsn["main"]["area_x"] + jsn["main"]["area_w"]])

        Result_data.append([base,peak_av,peak_index,rise,decay,area])
    return Result_data

def NormalOutput():
    print("normal")
    num_samples = int(100e5)
    sample_rate = 500e5
    frequency = sample_rate / num_samples

        # Generate time array and sine wave
    t = np.linspace(0, np.pi, num_samples, endpoint=False)
    sine_wave = np.sin(frequency * 2 * np.pi * t)
    sine_wave2 = np.sin(frequency * 2 * np.pi * t)
    waves=[sine_wave,sine_wave2]
    ReadPulse(waves)
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
        pulses=[]
        pulse_numbers=[]
        for path in pulse_pathes:
            pattern = fr'CH{ch}_(\d+).dat'
            match = re.search(pattern, path)
            pulse_numbers.append(match.group(1))
            with open(path, "rb") as fb:
                fb.seek(4)
                data = np.frombuffer(fb.read(), dtype="float64")
                pulses.append(data)

        results=ReadPulse(pulses)
        columns=["base","height","peak_index","rise","decay","area"]
        df = pd.DataFrame(results,columns=columns,index=pulse_numbers)
        df.to_csv(f"{Data_path}/CH{ch}_pulse/output.csv")    

        

NormalOutput()
