#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
from scipy.signal import medfilt
import pandas as pd
from scipy import stats 


# In[2]:


FREQ = 20 
WINDOW = 4
SEGMENT_SIZE = FREQ * WINDOW
OVERLAP = 60

SENSOR_COLS = ["ax", "ay", "az", "p", "r"]
MAX_VALUE = 32768 # 32768
TARGET_COL = "target"


# In[3]:


def median_filter(arr):
    values = np.asarray(arr)
    med_filtered = medfilt(values, kernel_size=3)
    return np.asarray(med_filtered)


# In[4]:


def normalise(arr): 
    global MAX_VALUE
    final_vals = np.round(arr / MAX_VALUE, 16)
    return np.asarray(final_vals, dtype=np.float64)


# In[5]:


def segmentation(df): 
    global SEGMENT_SIZE, OVERLAP, SENSOR_COLS, FREQ, WINDOW, TARGET_COL
    ncols = FREQ * WINDOW * len(SENSOR_COLS)
    segments = []
    labels = []
    # In each iteration, the row jumps by the overlap size
    # grab all rows of feature column values corresponding to length of segment 
    # grab corresponding mode of targetCol
    for row in range(0, len(df) - SEGMENT_SIZE, OVERLAP):
        window = []
        for col in SENSOR_COLS: 
            vals = np.asarray(df[row:row+SEGMENT_SIZE][col]) # each col's raw sensor values
            filtered_vals = median_filter(vals) # filtered 
            normalised_vals = normalise(filtered_vals) # normalised 
            window.append(normalised_vals) # each window extracted 
        segments.append(window) # 3d list of windows 
        label = stats.mode(df[row:row+SEGMENT_SIZE][TARGET_COL])[0][0]
        labels.append(label)
    
    segments = np.asarray(segments).reshape(-1,ncols) # reshaped 
    labels = np.asarray(labels)
    return segments, labels

