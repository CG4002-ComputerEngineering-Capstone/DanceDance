#!/usr/bin/env python
# coding: utf-8

# In[1]:


import math
import numpy as np
import pandas as pd
import scipy as sp

from scipy import stats
from scipy.fftpack import fft
from scipy.signal import medfilt
from scipy.fftpack import fft 
from scipy.fftpack import fftfreq 
from scipy.fftpack import ifft 
from numpy.fft import *
from scipy import fftpack


# In[2]:


SAMPLING_FREQ = 20 # Hz 
WINDOW_SIZE = 1 # sec 
OVERLAP = 10 # 10 steps forward and 10 steps from prev window 
SEGMENT_SIZE = SAMPLING_FREQ * WINDOW_SIZE # 20
FEATURE_COLS_LEN = 12 
FEATURE_COLS = ['t_body_acc_X','t_body_acc_Y','t_body_acc_Z',
                't_grav_acc_X','t_grav_acc_Y','t_grav_acc_Z',
                't_body_gyro_X','t_body_gyro_Y','t_body_gyro_Z',
                't_body_acc_mag','t_grav_acc_mag','t_body_gyro_mag']

TRAIN_MAX = {'acc_X': 1.27,
             'acc_Y': 1.27,
             'acc_Z': 1.27,
             'gyro_X': 276.28,
             'gyro_Y': 289.32,
             'gyro_Z': 271.8
            }

CUTOFF = 0.3 
MAXFREQ = 10 

SENSOR_COLS = ["acc_X", "acc_Y", "acc_Z", "gyro_X", "gyro_Y", "gyro_Z"]
SENSOR_COLS_LEN = 6

CUMULATIVE_DATA = np.zeros((1,SENSOR_COLS_LEN), dtype=float, order='C') # holds rows of live sensor data sent 
CUMULATIVE_DATA = np.delete(CUMULATIVE_DATA, 0,axis=0)


# In[3]:


def segmentator():
    """
    Extract segments using fixed-width sliding windows of size 1s. 
    Return: 3D Numpy array of size : n segments * 6 axial cols * 20 rows 
    """
    global CUMULATIVE_DATA, OVERLAP, SEGMENT_SIZE,SENSOR_COLS_LEN 
    
    # loop through the 2d array of nrows * 6
    # capture each column ==> len of each col = 20 and there should 6 cols ==> this will be the first segment 
    # segments will be a n segments * 6 col * 20 values 
    
    segments = []
    for row in range(0, len(CUMULATIVE_DATA)-(SEGMENT_SIZE-1), OVERLAP): 
#         print(f"Sampling row:{row} to row:{row+SEGMENT_SIZE}")
        windows = []
        for col in range(0,SENSOR_COLS_LEN):
            windows.append(CUMULATIVE_DATA[row:row+SEGMENT_SIZE,col])
#         print("Shape of Window: ", np.asarray(windows).shape)
        segments.append(windows)
#     print("Shape of segments : ", np.asarray(segments).shape)
    CUMULATIVE_DATA = np.delete(CUMULATIVE_DATA, np.s_[0:OVERLAP], axis = 0) 
    reshaped_segments = np.asarray(segments,dtype =np.float32).reshape(-1,SEGMENT_SIZE,SENSOR_COLS_LEN)
    return reshaped_segments


# In[4]:


def normaliseData(dframe):
    """
    Normalize axial features (values between 0 and 1). Columns rounded to 4dp after normalisation.
    Input: raw sensor data dframe 
    No return value
    """
    
    global SENSOR_COLS, TRA
    
    pd.options.mode.chained_assignment = None  # default='warn'
    for col in SENSOR_COLS:
        dframe[col] = dframe[col].div(100).round(6) # received sensor data were scaled by 100
        dframe[col] = dframe[col] / TRAIN_MAX[col]
        dframe[col] = dframe[col].round(4)


# In[5]:


def filter_signal(signal):
    """
    Applies 3rd order median filter for each signal i.e. Each axial column in dataset.
    Input: 1D Numpy array i.e. one column
    Return: 3rd order median-filtered signal i.e 1D Numpy array
    """
    array = np.array(signal)   
    med_filtered = medfilt(array, kernel_size=3) 
    return  med_filtered 


# In[6]:


def mag_3_signals(x,y,z): 
    """
    Finding Euclidian magnitude of 3-axial signal values of each row i.e. each sample point.
    Inputs: x, y , z columns (1D Numpy arrays)
    Return: Euclidian magnitude of each 3-axial signals
    """
    return [math.sqrt((x[i]**2+y[i]**2+z[i]**2)) for i in range(len(x))]


# In[7]:


def t_domain_feature_per_signal(t_signal):
    """
    For each time-domain signal, i.e. accx,y,z and gyrox,y,z, split into their respective time-domain components.
    Input: t_signal i.e. 1D Numpy array (time domain signal - each column)
    Returns: (total_component, t_DC_component , t_body_component, t_noise)
    """
    
    global CUTOFF, MAXFREQ, SAMPLING_FREQ
    
    t_signal = np.array(t_signal)
    t_signal_length = len(t_signal) 
#     print("number of sample points in t_signal", t_signal_length) 
    
    # 1D numpy array containing complex values
    f_signal = fft(t_signal) 
    
    # generate frequencies associated to f_signal complex values
    # frequency values between [-10hz:+10hz]
    freqs = np.array(sp.fftpack.fftfreq(t_signal_length, d = 1/float(SAMPLING_FREQ))) 
#     print("printing max freq under t_dom_feat_per_sig", freqs.max())
#     print("printing min freq under t_dom_feat_per_sig", freqs.min())
    f_DC_signal = [] # DC_component in freq domain
    f_body_signal = [] # body component in freq domain 
    f_noise_signal = [] # noise in freq domain
    
    # iterate over all available frequencies
    for i, freq in enumerate(freqs):
          
        # selecting the f_signal value associated to freq
        value = f_signal[i]
        
        # Selecting DC_component values 
        if abs(freq) > CUTOFF:
            f_DC_signal.append(float(0))                                       
        else: 
            f_DC_signal.append(value) 
    
        # Selecting noise component values 
        if (abs(freq) <= MAXFREQ):
            f_noise_signal.append(float(0))  
        else:
            f_noise_signal.append(value) 

        # Selecting body_component values 
        if (abs(freq) <= CUTOFF or abs(freq) > MAXFREQ):
            f_body_signal.append(float(0))
        else:
            f_body_signal.append(value) 
    
   
    t_DC_component = ifft(np.array(f_DC_signal)).real
    t_body_component = ifft(np.array(f_body_signal)).real
    t_noise = ifft(np.array(f_noise_signal)).real
    
    # extracting the total component(filtered from noise)
    total_component = t_signal - t_noise  
                                     
    return (total_component,t_DC_component,t_body_component,t_noise)


# In[8]:


def time_domain_feature_gen(df):
    """
    Add time domain features to df which contains normalised sensor values.
    Input : raw df i.e. segmented df with all 6 axial sensor values after being normalised
    Return : df with 12 cols appended from feature extraction 
    """    
    
    global SENSOR_COLS
    
    # iterate through all six axial signals 
    for column in SENSOR_COLS:
        t_signal = np.array(df[column])
        medfiltered_sig = filter_signal(t_signal)
        
        if 'acc' in column: 
            _,grav_acc,body_acc,_ = t_domain_feature_per_signal(medfiltered_sig) 
            df['t_body_'+ column] = body_acc
            df['t_grav_'+ column] = grav_acc 
            
        elif 'gyro' in column: 
            _,_,body_gyro,_ = t_domain_feature_per_signal(medfiltered_sig)
            df['t_body_gyro_'+ column[-1]] = body_gyro
    
    
    # all 9 axial signals generated above are reordered to facilitate find magnitude
    new_columns_ordered = ['t_body_acc_X','t_body_acc_Y','t_body_acc_Z',
                          't_grav_acc_X','t_grav_acc_Y','t_grav_acc_Z',
                          't_body_gyro_X','t_body_gyro_Y','t_body_gyro_Z']
    
    
    # Calculating magnitude by iterating over each 3-axial signal
    for i in range(0,9,3): 
        mag_col_name = new_columns_ordered[i][:-1]+'mag'
        x_col = np.array(df[new_columns_ordered[i]])   # copy X_component
        y_col = np.array(df[new_columns_ordered[i+1]]) # copy Y_component
        z_col = np.array(df[new_columns_ordered[i+2]]) # copy Z_component
        
        mag_signal = mag_3_signals(x_col,y_col,z_col) # calculate magnitude of each signal[X,Y,Z]
        df[mag_col_name] = mag_signal 
    
    return df 


# In[9]:


def getfinalSegs(segs):
    """
    Extract features for each window selected and convert into segments array
    Input: 3D Numpy segments array obtained after segmentation
    Return: 3D Numpy array with features extracted and raw cols removed
    """
    arr = np.asarray(segs)
    final_segs = []
    for r in range(0, arr.shape[0]):
        df = pd.DataFrame(arr[r], index=None, columns=SENSOR_COLS)
        normaliseData(df)
        df_feat = time_domain_feature_gen(df)
        final_segs.append(df_feat.drop(SENSOR_COLS, axis = 1).values)
    return np.asarray(final_segs)


# In[10]:


def getInputVector(finalSegs):
    """
    Get the input vector to be fed into nn.
    Input: finalSegs after feature extraction 
    Return: Input vector of shape n windows * (20*1*12)
    Note: num of windows, n = (len(df) / overlap) - 1, if you take first window as w1, else it will be (len(df) / overlap) - 2
    """
    global SAMPLING_FREQ, WINDOW_SIZE, FEATURE_COLS_LEN
    
    num_of_input_features = SAMPLING_FREQ * WINDOW_SIZE * FEATURE_COLS_LEN
    inputVector = finalSegs.reshape(finalSegs.shape[0], num_of_input_features)
    
    return inputVector.astype("float32")


# In[11]:


def resetCumData():
    """
    Function to be called before the start of dance move execution. Resets CUMULATIVE_DATA to empty numpy arr. 
    """
    global CUMULATIVE_DATA, SENSOR_COLS_LEN
    
    # holds rows of sensor data with 6 axial cols
    CUMULATIVE_DATA = np.zeros((1,SENSOR_COLS_LEN), dtype=float, order='C')  
    CUMULATIVE_DATA = np.delete(CUMULATIVE_DATA, 0,axis=0)


# In[12]:


def append(data):
    """
    Each row of live sensor data of 6 axial values, will be appended to a global 2D Numpy array. 
    From the global 2D Numpy array, a window of readings will be selected 
    to form an input vector of shape n x 240 to be fed into the nn.
    Input: data, i.e. 2D Numpy array of shape (20,6) is preferred 
    Returns: n x (20 * 12) Numpy array to be fed as input to nn model, where n is the number of windows
    """
    global CUMULATIVE_DATA , SENSOR_COLS_LEN, SEGMENT_SIZE 
    arr = np.array(data)
    
    # padding 
    if len(arr) < SEGMENT_SIZE:
        leftover = SEGMENT_SIZE - len(arr)
        padding = np.zeros((leftover, SENSOR_COLS_LEN),dtype=float, order='C')
        arr = np.concatenate((arr,padding))
        
    CUMULATIVE_DATA = np.concatenate((CUMULATIVE_DATA, arr))
#     print("GLOBAL ARRAY SHAPE BEFORE SEGMENTATION : ", CUMULATIVE_DATA.shape)
    segs = segmentator()
#     print("GLOBAL ARRAY SHAPE AFTER SEGMENTATION : ", CUMULATIVE_DATA.shape)
    fin_segs = getfinalSegs(segs)
    iv = getInputVector(fin_segs)
    
    return iv


# In[13]:


# # for testing 
# resetCumData()
# df = pd.read_csv("./capstone_data/test/dab_sean_1.csv", index_col=None, header = None )
# iv = append(np.asarray(df.values[0:20, 0:6]))
# print("input vector shape:", iv.shape)


# In[14]:


# iv = append(np.asarray(df.values[20:40, 0:6]))
# print("input vector shape:", iv.shape)


# In[15]:


# iv = append(np.asarray(df.values[40:60, 0:6]))
# print("input vector shape:", iv.shape)

