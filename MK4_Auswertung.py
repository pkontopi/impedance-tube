import numpy as np

import csv

from scipy.signal import butter, lfilter

#from scipy.stats import norm

#import plotly.graph_objects as go

#import json

# Parallelisierung
import concurrent.futures

def pathfinder(path, meas_count):
    csv_paths = []
    for i in range(1, meas_count+1): 
        csv_paths.append(path+str(i)+'.csv')

    return csv_paths

def butter_bandpass(f_low, f_high, fs, order=5):
    return butter(order, [f_low, f_high], fs=fs, btype='band')

def butter_bandpass_filter(data, f_low, f_high, fs, order=5):
    b, a = butter_bandpass(f_low, f_high, fs, order=order)
    output = lfilter(b, a, data)
    return output

def loaddata(csv_path, n):
    len_data = 1750
    #filtered_data = []
    
    #ave_arr = np.array([None]*(len(row_as_int)-n))

    r = np.array([None]*len_data)
    mini = np.array([None]*len_data)
    maxi = np.array([None]*len_data)

    with open(csv_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        index = 0
        for row in csvreader:
            row_as_int = [int(value) for value in row]
            
            #print(index)

            #Filter: 
            f_low = float(245+index)
            f_high = float(255+index)
            
            # Periode mal 2, nur so zur Sicherheit :)
            n = int((44100/(250+index))*2)

            row_as_int = butter_bandpass_filter(row_as_int, f_low, f_high, fs, order=3)

            row_as_int = row_as_int[10000:len(row_as_int)-10000]

            #filtered_data.append(row_as_int)
            
            ave_arr = []
            for k in range(len(row_as_int)-n):
                ave_arr.append(sum(np.abs(row_as_int[k:k+n]))/n)

            mini[index] = np.min(ave_arr)
            maxi[index] = np.max(ave_arr)

            swr = np.min(ave_arr)/np.max(ave_arr)

            r[index] = (1-swr)/(1+swr)
            
            index += 1
            print(index)
    #return filtered_data
    return r, mini, maxi
'''
def minimax(data, n): 
    ave_arr = np.array([None]*(len(data[0])-n))

    maxi = np.array([None]*len(data))
    mini = np.array([None]*len(data))

    r = np.array([None]*len(data))

    for i in range(len(data)):
        for k in range(len(data[0])-n):
            ave_arr[k] = sum(np.abs(data[i][k:k+n]))/n

        maxi[i] = np.max(ave_arr)
        mini[i] = np.min(ave_arr)

        swr = mini[i]/maxi[i]

        #swr = np.min(ave_arr)/np.max(ave_arr)

        r[i] = (1-swr)/(1+swr)
        
        print("r: "+str(r[i]))
        print(i)

    return r, maxi, mini
'''