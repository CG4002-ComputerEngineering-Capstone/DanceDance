#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from scipy.signal import medfilt


# In[2]:


SAMPLING_FREQ = 20 # Hz 
WINDOW_SIZE = 2 # sec 
OVERLAP = 20 
SEGMENT_SIZE = SAMPLING_FREQ * WINDOW_SIZE # 40

SENSOR_COLS = ["acc_X", "acc_Y", "acc_Z", "gyro_X", "gyro_Y", "gyro_Z", "yaw", "pitch", "roll"]

TRAIN_MAX = {'acc_X': 1.27,
             'acc_Y': 1.27,
             'acc_Z': 1.27,
             'gyro_X': 292.05,
             'gyro_Y': 289.32,
             'gyro_Z': 269.42,
             'yaw': 327.65,
             'pitch': 16.97,
             'roll': 15.87
            }


CUMULATIVE_DATA = np.zeros((1,len(SENSOR_COLS)), dtype=float, order='C') # holds rows of live sensor data sent 
CUMULATIVE_DATA = np.delete(CUMULATIVE_DATA, 0,axis=0)


# In[3]:


# def filter_input(arr):
#     """
#     Applies 3rd order median filter for each signal i.e. Each axial column in dataset.
#     Input: raw_input_arr of shape 40x6 appended 
#     """
    
#     global SENSOR_COLS
#     array = np.asarray(arr)
#     df = pd.DataFrame(array, index=None, columns=SENSOR_COLS)
    
#     for col in SENSOR_COLS: 
#         vals = np.array(df[col]) 
#         med_filtered = medfilt(vals, kernel_size=3) 
#         df[col] = med_filtered  
#     return df.values


# In[4]:


# def filter_signal(df):
#     """
#     Applies 3rd order median filter for each signal i.e. Each axial column in dataset.
#     Input: raw_df
#     """
    
#     global SENSOR_COLS
    
#     for col in SENSOR_COLS: 
#         array = np.array(df[col]) 
#         med_filtered = medfilt(array, kernel_size=3) 
#         df[col] = med_filtered  


# In[5]:


def normaliseData(dframe):
    """
    Normalize features for data (values between -1 and 1). Columns rounded to 4dp after normalisation.
    Input: raw sensor dframe 
    """
    
    global SENSOR_COLS, TRAIN_MAX
    
    pd.options.mode.chained_assignment = None  # default='warn'
    for col in SENSOR_COLS:
        dframe[col] = dframe[col].div(100).round(6)
        dframe[col] = dframe[col] / TRAIN_MAX[col]
        dframe[col] = dframe[col].round(4)


# In[6]:


def segmentator():
    """
    Extract segments using fixed-width sliding windows of size 2s. 
    Return: 3D Numpy array of size : n segments * 40 rows * 9 axial cols
    """
    global CUMULATIVE_DATA, OVERLAP, SEGMENT_SIZE,SENSOR_COLS
    
    # loop through the 2d array of nrows * 9
    # capture each column ==> len of each col = 40 and there should 9 cols ==> this will be the first segment 
    # segments will be a n segments * 9 col * 40 values 
    
    segments = []
    for row in range(0, len(CUMULATIVE_DATA)-(SEGMENT_SIZE-1), OVERLAP): 
#         print(f"Sampling row : {row} to row : {row+SEGMENT_SIZE}")
        windows = []
        for col in range(0,len(SENSOR_COLS)):
            windows.append(CUMULATIVE_DATA[row:row+SEGMENT_SIZE,col])
#         print("Shape of Window: ", np.asarray(windows).shape)
        segments.append(windows)
#     print("Shape of segments : ", np.asarray(segments).shape)
    CUMULATIVE_DATA = np.delete(CUMULATIVE_DATA, np.s_[0:OVERLAP], axis = 0) 
    reshaped_segments = np.asarray(segments,dtype =np.float32).reshape(-1,SEGMENT_SIZE,len(SENSOR_COLS))
    return reshaped_segments


# In[7]:


def getfinalSegs(segs):
    """
    Filter and Normalise each window selected.
    Input: 3D Numpy segments array obtained after segmentation
    Return: 3D Numpy array upon normalisation
    """
    arr = np.asarray(segs)
    final_segs = []
    for r in range(0, arr.shape[0]):
        df = pd.DataFrame(arr[r], index=None, columns=SENSOR_COLS)
     #   filter_signal(df)
        normaliseData(df)
        final_segs.append(df.values)
    return np.asarray(final_segs)


# In[8]:


def getInputVector(finalSegs):
    """
    Get the input vector to be fed into nn.
    Input: finalSegs after filtering and normalisation 
    Return: Input vector of shape n windows * (20*2*12)
    """
    global SAMPLING_FREQ, WINDOW_SIZE, SENSOR_COLS
    
    num_of_input_features = SAMPLING_FREQ * WINDOW_SIZE * len(SENSOR_COLS)
    inputVector = finalSegs.reshape(finalSegs.shape[0], num_of_input_features)
    
    return inputVector.astype("float32")


# In[9]:


def append(data):
    """
    Each row of live sensor data of 9 axial values, will be appended to a global 2D Numpy array. 
    From the global 2D Numpy array, a window of readings will be selected 
    to form an input vector of shape n x 360 to be fed into the nn.
    Input: data, i.e. 2D Numpy array of shape (40,6) is preferred 
    Returns: n x (40 * 9) Numpy array to be fed as input to nn model, where n is the number of windows
    """
    global CUMULATIVE_DATA , SEGMENT_SIZE, SENSOR_COLS
    arr = np.array(data)
    
    # padding 
    if len(arr) < SEGMENT_SIZE:
        leftover = SEGMENT_SIZE - len(arr)
        padding = np.zeros((leftover, len(SENSOR_COLS) ),dtype=float, order='C')
        arr = np.concatenate((arr,padding))
        
    #filtered_arr = np.asarray(filter_input(arr))
    CUMULATIVE_DATA = np.concatenate((CUMULATIVE_DATA, arr))
    print("GLOBAL ARRAY SHAPE BEFORE SEGMENTATION : ", CUMULATIVE_DATA.shape)
    segs = segmentator()
    print("GLOBAL ARRAY SHAPE AFTER SEGMENTATION : ", CUMULATIVE_DATA.shape)
    fin_segs = getfinalSegs(segs)
    iv = getInputVector(fin_segs)
    
    return iv


# In[10]:


def resetCumData():
    """
    Function to be called before the start of dance move execution. Resets CUMULATIVE_DATA to empty numpy arr. 
    """
    global CUMULATIVE_DATA, SENSOR_COLS
    
    # holds rows of sensor data with 9 axial cols
    CUMULATIVE_DATA = np.zeros((1,len(SENSOR_COLS)), dtype=float, order='C')  
    CUMULATIVE_DATA = np.delete(CUMULATIVE_DATA, 0,axis=0)


# In[11]:


# # for testing 
# resetCumData()
# df = pd.read_csv("./capstone_data/test/jamesbond_matthew_1.csv", index_col=None, header = None )
# iv = append(np.asarray(df.values[0:40, 0:9]))
# print("input vector shape:", iv.shape)


# In[12]:


# iv = append(np.asarray(df.values[40:80, 0:9]))
# print("input vector shape:", iv.shape)
# print(list(iv[0]))


# In[13]:


# iv = append(np.asarray(df.values[40:60, 0:9]))
# print("input vector shape:", iv.shape)

