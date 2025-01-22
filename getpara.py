# 解析用のプログラム

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.fftpack as fft
from scipy.optimize import curve_fit
import scipy.optimize
from scipy import signal
import shutil
import os
import re
import json
import warnings
import math
from natsort import natsorted
import glob
import plt_config

test_data = "E:/matsumi/data/20230512/room2-2_140mK_870uA_gain10_trig0.4_500kHz/CH0_pulse/rawdata/CH0_4800.dat"

e = 2.718
# ---解析プログラム作成------------------------------------------------------------

# --- Initialize ------------------------------------------------


# --- FILE LIBRARY ----------------------------------------------
# read binary data (also text)
def loadbi(path, type):
	if type == "binary":
		with open(path, "rb") as fb:
			fb.seek(4)
			data = np.frombuffer(fb.read(), dtype="float64")
	elif type == "text":
		data = loadtxt(path)
	return data


# read text data
def loadtxt(path):
	with open(path, "r") as f:
		data = np.loadtxt(f, comments="#", skiprows=6)
	return data


# read date data
def loaddate(path):
	with open(path, "r") as f:
		data = f.readline()
	return data


# tranceform settingfile from text to Json
def setting_json(path, ch):
	setting = np.loadtxt("Setting.txt", skiprows=10)
	setting_json = {
		"path": path,
		"channel": ch,
		"rate": int(setting[2]),
		"samples": int(setting[4]),
		"presamples": int(setting[5]),
		"threshold": setting[6],
	}
	set = json.dumps(setting_json, indent=4)
	return set


# read Json file
def loadJson():
	with open("setting.json") as f:
		jsn = json.load(f)
	return jsn


# save Json file
def saveJson(setting, path):
	jsn = json.dumps(setting, indent=4)

	# home directry
	with open(f"{os.path.dirname(__file__)}/../setting.json", "w") as file:
		file.write(jsn)

	# output directry
	with open(f"{path}/setting.json", "w") as file:
		file.write(jsn)


# read Index file (ex selected_index.txt)
def loadIndex(path):
	index = []
	try:
		with open(path, "r") as f:
			for row in f.read().splitlines():
				index.append(row)
		return [int(i) for i in index]
	except:
		with open(path, "r") as f:
			for row in f.read().splitlines():
				index.append(row)
		return [int(float(i)) for i in index]


# load PHITS .out file
# start, end is row you wanna extruct
def loadPHITS(path, start, end, column):
	with open(path, "r") as f:
		n = 0
		electron = []
		for i in f.readlines():
			if n > start - 2 and n < end:
				ele = i.split("  ")[1:][column]
				electron.append(float(ele))
			n += 1
	return electron

def globsort(path):
	return natsorted(glob.glob(path))

# ---------------------------------------------------------------------


def select_condition(df, select):
	if "index" in select:
		
		selectdata = loadIndex(select["index"])
		df = df[df.index.isin(selectdata)]

	
	for i in select:
		try:
			param, sym = i.split("-")
			if i == "index->":
				df = df.iloc[select[i] :]
			elif i == "index-<":
				df = df.iloc[: select[i]]
			else:
				if sym == ">":
					df = df[df[param] > select[i]]
				elif sym == "<":
					df = df[df[param] < select[i]]
				elif sym == "=":
					df = df[df[param] == select[i]]
				elif sym == "!":
					df = df[df[param] != select[i]]
		except Exception as e:
			continue
	return df


def overlap(df_0, df_1):
	df_comp_0 = df_0[df_0.index.isin(df_1.index)]
	df_comp_1 = df_1[df_1.index.isin(df_0.index)]
	return df_comp_0, df_comp_1


def data_time(rate, samples):
	return np.arange(0, 1 / rate * samples, 1 / rate)


# ---- MAIN LIBRARY ------------------------------------------


# ベースラインを作成
def baseline(data, presamples, x, w):
	base = np.mean(data[presamples - x : presamples - x + w])
	data_ba = data - base
	return base, data_ba


# ピークの検出
def peak(data, presamples, w_max, x_av, w_av):
	peak = np.max(data[presamples : presamples + w_max])
	peak_index = np.argmax(data[presamples : presamples + w_max]) + presamples
	peak_av = np.mean(data[peak_index - x_av : peak_index - x_av + w_av])
	return peak, peak_av, peak_index


# 積分
def integrate(data):
	return np.sum(data)


# ライズタイム
def risetime(data, peak, peak_index, rise_high,rise_low,rate):
	rise_90 = 0
	rise_10 = 0

	for i in reversed(range(0, peak_index)):
		if data[i] <= peak * rise_high:
			rise_90 = i
			break

	for j in reversed(range(0, rise_90)):
		if data[j] <= peak * rise_low:
			rise_10 = j
			break

	# rise_90 = np.argmax(data[peak_index-500:peak_index]>=peak*0.9)+peak_index-500
	# rise_10 = np.argmax(data[peak_index-500:peak_index]>=peak*0.1)+peak_index-500
	rise = (rise_90 - rise_10) / rate
	return rise, rise_10, rise_90


# ディケイタイム
def decaytime(data, peak, peak_index, decay_high,decay_low,rate):
	decay_90 = 0
	decay_10 = 0
	for i in range(peak_index, len(data)):
		if data[i] <= peak * decay_high:
			decay_90 = i
			break
	for j in range(decay_90, len(data)):
		if data[j] <= peak * decay_low:
			decay_10 = j
			break

	# decay_90 = np.argmax(data[peak_index:]<=peak*0.9)
	# decay_10 = np.argmax(data[peak_index:]<=peak*0.1)
	decay = (decay_10 - decay_90) / rate
	return decay, decay_10, decay_90


def area(data, peak_index, x, w):
	return np.sum(data[peak_index - x : peak_index - x + w])

def arrival_time_threshold(data,threshold):
	return np.argmax(data >= threshold)

def arrival_time(data,presamples,x,w):
	diff = np.argmax(gp.diff(data[presamples:])) + presamples
	fit_data = data[diff-x:diff-x+w]
	fit_range = np.arange(diff-x,diff-x+w,1)
	popt,ccpov = curve_fit(gp.multi_func,fit_range,fit_data,p0=[0,0])
	arrival = -popt[0]/popt[1]
	return arrival

def arrival_time_2(data,point,x,w):
	fit_data = data[point-x:point-x+w]
	fit_range = np.linspace(point-x,point-x+w,w)
	popt,ccpov = curve_fit(multi_func,fit_range,fit_data,p0=[0,0])
	arrival = -popt[1]/popt[0]
	return arrival
	

# LP Filter
def BesselFilter(x, rate, fs):
	# fn = rate/2
	# ws = fs/fn
	ws = fs / rate * 2
	b, a = signal.bessel(2, ws, "low")
	y = signal.filtfilt(b, a, x)
	return y


# 移動平均
def moving_average(x, w):
	return np.convolve(x, np.ones(w), "valid") / w


# 微分
def diff(data):
	return np.gradient(data)


def valid_convolve(xx, size):
    b = np.ones(size)/size
    xx_mean = np.convolve(xx, b, mode="same")

    n_conv = math.ceil(size/2)

    # 補正部分
    xx_mean[0] *= size/n_conv
    for i in range(1, n_conv):
        xx_mean[i] *= size/(i+n_conv)
        xx_mean[-i] *= size/(i + n_conv - (size % 2)) 
	# size%2は奇数偶数での違いに対応するため

    return xx_mean


# フィルター処理
def filter(data, rate, samples):
	fq = np.arange(0, rate, rate / samples)
	f = np.fft.fft(data)
	F = np.abs(f)
	# graugh_fft('fft',F[:int(samples/2)+1],fq[:int(samples/2)+1])
	graugh_fft("fft", F, fq)
	filter = np.linspace(1, 1, int(samples))
	cutoff_l = input("Enter low cutoff freqency(Hz)")
	cutoff_h = input("Enter hight cutoff freqency(Hz)")
	f2 = np.copy(f)
	for i in range(len(fq)):
		index_1 = 0
		if fq[i] >= int(cutoff_l):
			index_1 = i
			break
	for j in range(index_1, len(fq)):
		index_2 = 0
		if fq[j] >= int(cutoff_h):
			index_2 = j
			break
	filter[index_1:index_2] = 0
	f2 = f2 * filter
	F2 = np.abs(f2)
	ifft = np.fft.ifft(f2)
	# graugh_fft('fft',F2[:int(samples/2)+1],fq[:int(samples/2)+1])
	graugh_fft("fft", F2, fq)
	return ifft.real


def gausse(x, A, mu, sigma):
	return A * np.exp(-((x - mu) ** 2) / (2.0 * sigma**2))


def FWHW(sigma):
	return 2 * sigma * (2 * np.log(2)) ** (1 / 2)


# ---------- Fitting ---------------------------------------------------

# fitting parameter sample
#start = 0      # presamples + start
#width = 1000  #  start + width
#p0_2 = [-1.6,12,presamples,5570,presamples]
#p0_3 = [-1.6,12,presamples,5570,presamples,5000,presamples]
#p0_4 = [-1.6,12,presamples,5570,presamples,5000,presamples,5000,presamples]
#p0_5 = [-1.6,12,presamples,5570,presamples,12,presamples,12,presamples]

def multi_func(X, *params):
	Y = np.zeros_like(X)
	for i, param in enumerate(params):
		Y = Y + np.array(param * X**i)
	return Y


def fit_func(func):
	if func == "monoExp":
		return monoExp
	elif func == "doubleExp":
		return doubleExp
	elif func == "tripleExp":
		return tripleExp
	elif func == "forthExp":
		return forthExp
	elif func == "forthExp2":
		return forthExp2


# フィッティング
def monoExp(x, m, t):
	return m * np.exp(-t * x)


# Fitting entire pulse
def doubleExp(x, m, t1, b1, t2, b2):
	return m * (np.exp(-(x - b1) / t1) - np.exp(-(x - b2) / t2))


# Fitting entire pulse
def tripleExp(x, m, t1, b1, t2, b2, t3, b3):
	return m * (
		np.exp(-(x - b1) / t1) - np.exp(-(x - b2) / t2) - np.exp(-(x - b3) / t3)
	)


def forthExp(x, m, t1, b1, t2, b2, t3, b3, t4, b4):
	return m * (
		np.exp(-(x - b1) / t1)
		- np.exp(-(x - b2) / t2)
		- np.exp(-(x - b3) / t3)
		- np.exp(-(x - b4) / t4)
	)

def forthExp2(x, m, t1, b1, b2, t3, b3, t4, b4,t5, b5):
	return m * (
		np.exp(-(x - b1) / t1)
		- np.exp(-(x - b3) / t3)
		- np.exp(-(x - b4) / t4)
		- np.exp(-(x - b5) / t5)
	) + np.exp((x - b2))


def fitExp(func, data, start, width, p0):
	warnings.simplefilter("ignore")
	warnings.simplefilter("error", scipy.optimize.OptimizeWarning)
	warnings.simplefilter("error", scipy.optimize._optimize.OptimizeWarning)
	x = np.arange(start, start + width)
	y = data[start : start + width]
	try:
		params, cov = curve_fit(func, x, y, p0=p0, maxfev=10000)
		rSq = rSquared(y,func(x, *params))
	except (
		scipy.optimize.OptimizeWarning,
		scipy.optimize._optimize.OptimizeWarning,
		RuntimeError,
	):
		params = np.zeros(len(p0))
		rSq = 0
	return params, rSq

def rSquared(y,y_fit):
	squaredDiffs = np.square(y - y_fit)
	squaredDiffsFromMean = np.square(y - np.mean(y))
	rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
	return rSquared

# ---------------------------------------------------------------------------


def search_peak(hist):
	mv = moving_average(hist, 5)
	plt.plot(hist)
	plt.plot(mv)
	diff = moving_average(np.gradient(mv), 5)
	diff2 = np.gradient(diff)
	plt.plot(diff)

	# plt.show()
	min = int(input("range min: "))
	threshold = 1
	print("\n")

	trigger = False
	trigger2 = False
	peak_list = []
	for i in reversed(np.arange(min, len(hist) - 10, 1)):
		if trigger == False and diff[i] < threshold * -1:
			trigger = True
		if trigger == True and diff[i] > 0:
			if trigger2 == False:
				peak = []
				peak.append(np.max(hist[i : i + 10]))
				peak.append(np.argmax(hist[i : i + 10]) + i)
				trigger2 = True
			if trigger2 == True and diff2[i] > 0:
				peak.append((peak[1] - (i - 1)))
				peak_list.append(peak)
				trigger = False
				trigger2 = False

	return peak_list


# ----------グラフからデータを抽出---------------------------------
def pickSamples(df, x, y):
	coo = ginput(df[x], df[y])

	inside = np.ndarray(len(df[x]), dtype=bool)
	inside[:] = False
	for i, (sx, sy) in enumerate(zip(df[x], df[y])):
		inside[i] = inpolygon(sx, sy, coo[:, 0], coo[:, 1])
	# PlotSelected(x,y,inside,x_picked,y_picked)
	return df[inside].index.values.tolist()

def pickSamples_PoST(df_1,df_2, para):
	coo = ginput(df_1[para], df_2[para])

	inside = np.ndarray(len(df_1[para]), dtype=bool)
	inside[:] = False
	for i, (sx, sy) in enumerate(zip(df_1[para], df_2[para])):
		inside[i] = inpolygon(sx, sy, coo[:, 0], coo[:, 1])
	# PlotSelected(x,y,inside,x_picked,y_picked)
	return df_1[inside].index.values.tolist()


def extruct(df, *x):
	ext = []
	for i in x:
		ext.append(df.loc[:, i].values)
	return ext


def ginput(x, y):
	plt.plot(x, y, "bo", markersize=1)
	# plt.ylim(0,2)
	plt.grid()
	picked = plt.ginput(n=-1, timeout=-1)
	plt.show()
	plt.cla()

	return np.array(picked)


def inpolygon(sx, sy, x, y):
	inside = False
	for i1 in range(len(x)):
		i2 = (i1 + 1) % len(x)
		if min(x[i1], x[i2]) < sx < max(x[i1], x[i2]):
			if (y[i1] + (y[i2] - y[i1]) / (x[i2] - x[i1]) * (sx - x[i1]) - sy) > 0:
				inside = not inside
	return inside


def PlotSelected(x, y, inside, x_picked, y_picked):
	plt.plot(x[inside == True], y[inside == True], "gs", markersize=2)
	plt.plot(x[inside == False], y[inside == False], "ko", markersize=1, alpha=0.4)
	plt.ylim(0, 2)

	plt.grid()
	plt.show()
	plt.cla()


# --------------------------------------------------------------


# 平均パルスを作成
def average_pulse(index, set):
	array = []
	presamples = set["Config"]["presamples"]

	for i in index:
		try:
			data = loadbi(i)
		except:
			data = loadtxt(i)
		base, data = baseline(data, presamples, 1000, 500)
		array.append(data)
	av = np.mean(array, axis=0)
	return av


# -------- GRAUGH LIBRARY -------------------------------------
# パルスグラフ表示
def graugh(path, data, time):
	x = time
	y = data
	title = os.path.basename(path)
	plt.plot(x, y, label="data")
	plt.xlabel("time(s)")
	plt.ylabel("volt(V)")
	plt.title(title.replace(".dat", ""))

	# plt.legend()
	# plt.show()
	# plt.cla()


# パルスグラフ保存
def graugh_save(path, data, time):
	x = time
	y = data
	title = os.path.basename(path)
	plt.plot(x, y, label="data")
	plt.xlabel("time")
	plt.ylabel("volt")
	plt.title(title.replace(".dat", ""))
	plt.legend()
	plt.savefig(path.replace("rawdata", "output").replace(".dat", ""))
	plt.cla()


# パラメータグラフ表示
def graugh_para(x, y, x_ax, y_ax, color):
	plt.scatter(x, y, color=color, s=2)
	plt.xlabel(x_ax)
	plt.ylabel(y_ax)
	plt.title(f"{x_ax} vs {y_ax}")
	plt.grid()
	# plt.show()
	# plt.cla()


# 周波数グラフ表示
def graugh_fft(path, data, time):
	print("Click cutoff frequency.")
	x = time
	y = data
	title = os.path.basename(path)
	plt.plot(x, y, label="data")
	plt.xlabel("FQ(Hz)")
	plt.ylabel("AMP")
	plt.xscale("log")
	plt.yscale("log")
	plt.title(title.replace(".dat", ""))
	# a = plt.ginput(n=2,mouse_add=1,mouse_pop=3,mouse_stop=2)
	plt.show()


def graugh_condition(graugh):
	plt.xlim(graugh["xlim->"], graugh["xlim-<"])
	if graugh["log"]:
		plt.yscale("log")


# ------------------------------------------------------------------


# outputフォルダの作成
def output(path, df):
	if not os.path.exists(path):
		os.mkdir(path)
		df.to_csv(os.path.join(path, "output.csv"))
	else:
		replace = input("Replace output folder? (Yes -> [0], No (not save) -> [1])")
		if replace == "0":
			shutil.rmtree(path)
			os.makedirs(path)
			df.to_csv(os.path.join(path, "output.csv"))


# ダブルパルス除去（仮）
def double_event(data, threshold):
	dif = diff(data)
	cnt = 0
	a = 1
	while a == 1:
		pre = np.max(dif[: len(dif) / 2])
		post = np.max(dif[len(dif) / 2 :])
		if pre < threshold:
			dif = dif[len(dif) / 2 :]
		if post < threshold:
			dif = dif[: len(dif) / 2]

	plt.plot(dif)
	plt.show()


# extruct numbers from strings
def num(strings):
	return re.findall(r"\d+", strings)


ax_unit = {
	"base": "base[V]",
	"height": "pulse height[V]",
	"peak_index": "peak index",
	"height_opt": "pulse height opt",
	"height_opt_temp": "pulse height opt temp",
	"rise": "rise[s]",
	"decay": "decay[s]",
	"rise_fit": "rise_fit[s]",
	"tau_rise": "tau_rise[s]",
	"tau_decay": "tau_decay[s]",
	"rSquared": "rSquared",
}


def main():
	data = loadbi(test_data)
	filt = BesselFilter(data, 1e6, 1e4)
	double_event(filt, 0.005)


if __name__ == "__main__":
	main()
