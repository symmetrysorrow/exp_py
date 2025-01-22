import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.fftpack as fft
from scipy import signal
import shutil
import os

def hanning(data,samples):
    han = signal.hann(samples)                    # ハニング窓作成
    acf = 1 / (sum(han) / samples)
    data = data*han
    return data,acf  


def BesselFilter(x,rate,fs):
    fn = rate/2
    ws = fs/fn
    b,a = signal.bessel(4,ws,"low")
    y = signal.filtfilt(b,a,x)
    return y



#fft
def fft_amp(data,samples,acf):
    f = fft.fft(data)
    amp = np.abs(f)*acf/(samples/2)
    return amp

def graugh_spe(data,fq):
    plt.plot(data,fq,label="data")
    plt.xlabel("Freaquency(Hz)")
    plt.ylabel('Intensity[pA/kHz$^{1/2}$]')
    plt.xscale('log')
    plt.yscale('log')
    plt.title('Average pulse spectrum')
    
    #a = plt.ginput(n=2,mouse_add=1,mouse_pop=3,mouse_stop=2)
    
    
def bandstop(x, rate, fp, fs, gpass, gstop):
    fn = rate / 2                           #ナイキスト周波数
    wp = fp / fn                                  #ナイキスト周波数で通過域端周波数を正規化
    ws = fs / fn                                  #ナイキスト周波数で阻止域端周波数を正規化
    N, Wn = signal.buttord(wp, ws, gpass, gstop)  #オーダーとバターワースの正規化周波数を計算
    b, a = signal.butter(N, Wn, "bandstop")       #フィルタ伝達関数の分子と分母を計算
    y = signal.filtfilt(b, a, x)                  #信号に対してフィルタをかける
    return y     



#フィルター処理
def filter(data,rate,samples):
    fq = np.arange(0,rate,rate/samples)
    f = np.fft.fft(data)
    F =np.abs(f)
    #graugh_fft('fft',F[:int(samples/2)+1],fq[:int(samples/2)+1])
    graugh_spe('fft',F,fq)
    filter =np.linspace(1,1,int(samples))
    cutoff_l= input('Enter low cutoff freqency(Hz)')
    cutoff_h= input('Enter hight cutoff freqency(Hz)')
    f2 = np.copy(f)
    for i in range(len(fq)):
        index_1 = 0
        if fq[i] >= int(cutoff_l):
            index_1 = i
            break
    for j in range(index_1,len(fq)):
        index_2 = 0
        if fq[j] >= int(cutoff_h):
            index_2 = j
            break
    filter[index_1:index_2] = 0
    f2 = f2*filter
    f2[(f2<10)]=0
    print(f2)
    F2 =np.abs(f2)
    ifft = np.fft.ifft(f2)
    graugh_fft('fft',F2[:int(samples/2)+1],fq[:int(samples/2)+1])
    graugh_spe('fft',F2,fq)
    return ifft.real 

