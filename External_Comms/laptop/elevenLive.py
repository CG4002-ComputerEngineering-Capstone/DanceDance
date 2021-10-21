#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
from scipy.signal import medfilt
import pandas as pd


# In[2]:


FREQ = 20 
WINDOW = 2
SEGMENT_SIZE = FREQ * WINDOW
OVERLAP = 20

SENSOR_COLS = ["ax", "ay", "az", "p", "r"]
MAX_VALUE = 32768 # 32768

DATA = np.zeros((1,len(SENSOR_COLS)),dtype=np.float64)
# DATA = np.delete(DATA, 0,axis=0)


# In[3]:


def segmentation(): 
    global DATA, SEGMENT_SIZE, OVERLAP, SENSOR_COLS, FREQ, WINDOW
    ncols = FREQ * WINDOW * len(SENSOR_COLS)
    segments = []
    for row in range(0, len(DATA) - SEGMENT_SIZE, OVERLAP):
        window = []
        for col in range(0, len(SENSOR_COLS)): 
            vals = DATA[row:row+SEGMENT_SIZE, col] # each col's raw sensor values
            filtered_vals = median_filter(vals) # filtered 
            normalised_vals = normalise(filtered_vals) # normalised 
            window.append(normalised_vals) # each window extracted 
        segments.append(window) # 3d list of windows 
    
    segments = np.asarray(segments).reshape(-1,ncols) # reshaped 
    DATA = np.delete(DATA, np.s_[0:OVERLAP], axis = 0) # pop first 50% overlap rows
    return segments


# In[4]:


def median_filter(arr):
    values = np.asarray(arr)
    med_filtered = medfilt(values, kernel_size=3)
    return np.asarray(med_filtered)


# In[5]:


def normalise(arr): 
    global MAX_VALUE
    final_vals = np.round(arr / MAX_VALUE, 16)
    return np.asarray(final_vals, dtype=np.float64)


# In[6]:


def append(inputArr):
    """
    Function returns inputVector to be fed into the nn.
    """
    
    global DATA , SEGMENT_SIZE, SENSOR_COLS
    arr = np.asarray(inputArr, dtype=np.float64)

    # padding 
    if len(arr) < SEGMENT_SIZE:
        leftover = SEGMENT_SIZE - len(arr)
        padding = np.zeros((leftover, len(SENSOR_COLS)),dtype=np.float64, order='C')
        arr = np.concatenate((arr,padding))
        
    DATA = np.concatenate((DATA, arr))
    print("GLOBAL ARRAY SHAPE BEFORE SEGMENTATION: ",DATA.shape)
    segs = segmentation()
    print("GLOBAL ARRAY SHAPE AFTER SEGMENTATION:  ",DATA.shape)
    return segs


# In[7]:


def resetCumData(): 
    """
    Function to be called before the start of every dance move.
    """
    global SENSOR_COLS, DATA
    
    DATA = np.zeros((1,len(SENSOR_COLS)),dtype=np.float64)


# In[8]:


# # usage
# resetCumData()
# df = pd.read_csv("../capstone_data/test2/dab_chekjun_5.csv", names= ["ax", "ay", "az", "y", "p", "r", "start_move", "checksum"], header=None, index_col=None)
# df.drop(columns=["y", "start_move", "checksum"], axis=1,inplace=True)
# df.reset_index(drop=True,inplace=True)
# iv = append(np.asarray(df[0:40]))


# In[9]:


# iv[0]


# In[10]:


# iv.shape

