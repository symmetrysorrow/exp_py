#2024/12/04 Hata&tagawa

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from scipy import signal
import shutil
from natsort import natsorted
import getpara as gp
import fft_spectrum as sp
import json
import pprint
import sys
import re
import matplotlib.cm as cm
import plt_config
import tqdm

path=""

def ReadPulse(pulses):
    with open(f"{path}/setting.json") as f:
        jsn = json.load(f)
    for pulse in pulses:
        ws = jsn["Setting"]["samples"] / jsn["Config"]["rate"] * 2
        b, a = signal.bessel(2, ws, "low")
        filtered_pulse = signal.filtfilt(b, a, pulse)

	

def NormalOutput():
    print("normal")
    pattern = re.compile(r'CH(\d+)_pulse')
    Channels = []
    for folder_name in os.listdir(path):
        match = pattern.match(folder_name)
        if match:
            # 数字部分を取得してリストに追加
            Channels.append(int(match.group(1)))

    for ch in Channels:
        pulse_pathes = natsorted(glob.glob(f'CH{ch}_pulse/rawdata/CH{ch}_*.dat'))
        pulses=[]
        for path in pulse_pathes:
            with open(path, "rb") as fb:
                fb.seek(4)
                data = np.frombuffer(fb.read(), dtype="float64")
                pulses.append(data)

        result=ReadPulse(pulses)
            

        


