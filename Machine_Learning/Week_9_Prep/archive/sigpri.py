#!/usr/bin/env python
# coding: utf-8

# In[1]:


import math
import glob
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
WINDOW_SIZE = 2 # seconds
OVERLAP = int((SAMPLING_FREQ * WINDOW_SIZE) / 2) # no of rows (readings) to drop from the front = no.of rows as steps forward  
NYQ = SAMPLING_FREQ / float(2) # Nyquist frequency 


CUTOFF = 0.3 
MAXFREQ = 10 

DANCE_MOVES = ["jamesbond", "dab", "mermaid"]
SENSOR_COLS = ["acc_X", "acc_Y", "acc_Z", "gyro_X", "gyro_Y", "gyro_Z"]

READING_SIZE = SAMPLING_FREQ * WINDOW_SIZE # received sensor data length = SEGMENT SIZE 
NUM_OF_LIVE_SENSOR_COLS = 6
FEATURE_COLS = 12 

CUMULATIVE_DATA = np.zeros((1,FEATURE_COLS), dtype=float, order='C') # holds rows of sensor data with 12 extracted cols
CUMULATIVE_DATA = np.delete(CUMULATIVE_DATA, 0,axis=0)


# In[3]:


def normaliseData(dframe):
    """
    Normalize features for training data set (values between 0 and 1). Columns rounded to 4dp after normalisation.
    Input: dframe 
    No return value
    """
    pd.options.mode.chained_assignment = None  # default='warn'
    for col in dframe.columns:
#         print(col)
        dframe[col] = dframe[col].div(100).round(6) # received sensor data were scaled by 100
        dframe[col] = dframe[col] / dframe[col].max()
        dframe[col] = dframe[col].round(4)


# In[4]:


def generateDframeForFeatureGeneration(array):
    """
    From the 40 x 6 Numpy Array, create a dframe, normalise 
    and prepare for feature generation. 
    Input : 2D Numpy array of shape 40 x 6 
    Return : df of shape 40 rows * 6 cols 
    """
    
    global SENSOR_COLS
    
    df = pd.DataFrame(data=array, index=None, columns=SENSOR_COLS)
    normaliseData(df)
    return df


# In[5]:


def filter_signal(signal):
    """
    Applies 3rd order median filter for each signal i.e. Each axial column in dataset.
    Input: 1D Numpy array for each axial column 
    Return: 3rd order median-filtered signal i.e.1D Numpy array 
    """
    array = np.array(signal)   
    med_filtered = medfilt(array, kernel_size=3) 
    return  med_filtered  


# In[6]:


def t_domain_feature_per_signal(t_signal):
    """
    For each time-domain signal, i.e. accx,y,z and gyrox,y,z, split into their respective time-domain components. 
    Pass the entire column and get the corresponding time domain components.
    Input: t_signal i.e. 1D Numpy array (time domain signal)
    Returns: (total_component, t_DC_component , t_body_component, t_noise)
    """
    
    global CUTOFF, MAXFREQ, SAMPLING_FREQ
    
    
    t_signal = np.array(t_signal)
    t_signal_length = len(t_signal) # num of sample pts in t_signal i.e. For e.g. 40 for received live sensor data 

    # 1D numpy array containing complex values
    f_signal = fft(t_signal) 
    
    # generate frequencies associated to f_signal complex values
    # frequency values between [-10hz:+10hz]
    freqs = np.array(sp.fftpack.fftfreq(t_signal_length, d = 1/float(SAMPLING_FREQ))) 
    
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


# In[7]:


def mag_3_signals(x,y,z): 
    """
    Finds Euclidian magnitude of 3-axial signal.
    Inputs: x, y , z columns (Numpy arrays)
    Return: Euclidian magnitude of each set of x,y,z i.e. each sample reading's mag
    """
    return [math.sqrt((x[i]**2+y[i]**2+z[i]**2)) for i in range(len(x))]


# In[8]:


def time_domain_feature_gen(df):
    """
    Generates as df with time domain features. This should yield 12 feature cols of data. 
    Input : df i.e. df containing 1 min readings of 6 axial data of each trial of a dance move 
    Returns : dframe with 12 axial values derived from raw data 
    """
    
    global SAMPLING_FREQ, CUTOFF, MAXFREQ
    
    time_sig = {}
    
    # iterate through all six axial signals 
    for column in df.columns:
        t_signal = np.array(df[column])
        medfiltered_sig = filter_signal(t_signal)
        
        if 'acc' in column: 
            _,grav_acc,body_acc,_ = t_domain_feature_per_signal(medfiltered_sig) 
            time_sig['t_body_'+ column] = body_acc
            time_sig['t_grav_'+ column] = grav_acc 
            
        elif 'gyro' in column: 
            _,_,body_gyro,_ = t_domain_feature_per_signal(medfiltered_sig)
            time_sig['t_body_gyro_'+ column[-1]] = body_gyro
    
    
    # all 9 axial signals generated above are reordered to facilitate finding magnitude
    new_columns_ordered = ['t_body_acc_X','t_body_acc_Y','t_body_acc_Z',
                          't_grav_acc_X','t_grav_acc_Y','t_grav_acc_Z',
                          't_body_gyro_X','t_body_gyro_Y','t_body_gyro_Z']
    
    
    # generate a new df from the time_sig dict
    ordered_time_sig_df = pd.DataFrame()
    for col in new_columns_ordered: 
        ordered_time_sig_df[col] = time_sig[col] 
    
    # Calculating magnitude by iterating over each 3-axial signal
    for i in range(0,9,3): 
        mag_col_name = new_columns_ordered[i][:-1]+'mag'
        x_col = np.array(ordered_time_sig_df[new_columns_ordered[i]])   # copy X_component
        y_col = np.array(ordered_time_sig_df[new_columns_ordered[i+1]]) # copy Y_component
        z_col = np.array(ordered_time_sig_df[new_columns_ordered[i+2]]) # copy Z_component
        
        mag_signal = mag_3_signals(x_col,y_col,z_col) # calculate magnitude of each signal[X,Y,Z]
        ordered_time_sig_df[mag_col_name] = mag_signal 
    
    return ordered_time_sig_df 


# In[9]:


def segment_global(): 
    """
    Extracts the required window from the global list. 
    Return : Extracted window of 2D array, i.e. expected 2D Numpy array of shape 40 * 12 
    """
    
    global CUMULATIVE_DATA, OVERLAP, READING_SIZE
    
    input_selected = CUMULATIVE_DATA[0:READING_SIZE] # 40 rows or data pts selected 
    CUMULATIVE_DATA = np.delete(CUMULATIVE_DATA, np.s_[0:OVERLAP], axis = 0) # pop first 20 
    return input_selected


# In[10]:


def getInputVector(arr):
    """
    Transform window of 40 data points into a single 1D array representing each window to be fed into nn. 
    Input: 2D Numpy arr of expected shape 40 * 12 
    Return: inputVector for nn, i.e. 1 x (40rows * 12features)
    """
    global READING_SIZE, FEATURE_COLS
    
#     segments = []
    ncols = READING_SIZE * FEATURE_COLS
#     for i in range(0,arr.shape[1]): 
#         segments.append(arr[:,i])
#     reshaped_segments = np.asarray(segments,dtype=np.float32).reshape(-1,READING_SIZE,FEATURE_COLS)
#     invec = reshaped_segments.reshape(reshaped_segments.shape[0], ncols)
    invec = arr.reshape(1, ncols)
    return invec.astype("float32")


# In[11]:


def append(data):
    """
    Each row of live sensor data of 6 axial values, will be pre-processed & extracted into 12 feature columns 
    and appended to a global 2D Numpy array. 
    From the global 2D Numpy array, a window of readings will be selected 
    to form a input vector of shape 1 x 480 to be fed into the nn.
    Input: data, i.e. 2D Numpy array of shape (40,6) is preferred 
    Returns: 1 x (40 * 12 ) Numpy array to be fed as input to nn model and it's shape
    """
    global CUMULATIVE_DATA , NUM_OF_LIVE_SENSOR_COLS, READING_SIZE
    
    
    arr = np.array(data)
    
    # padding 
    if len(arr) < READING_SIZE:
        leftover = READING_SIZE - len(arr)
        padding = np.zeros((leftover, NUM_OF_LIVE_SENSOR_COLS),dtype=float, order='C')
        arr = np.concatenate((arr,padding))
        
    # feature generation and update of global list 
    raw_df = generateDframeForFeatureGeneration(arr)
    df = time_domain_feature_gen(raw_df)
    CUMULATIVE_DATA = np.concatenate((CUMULATIVE_DATA, df.values))
    selected_window = segment_global()
    inputvector = getInputVector(selected_window)
    print("cumulative data shape: ", CUMULATIVE_DATA.shape)
    
    return (inputvector, inputvector.shape)


# In[12]:


def resetCumData():
    """
    Function to be called at the end of dance move execution. Resets CUMULATIVE_DATA to empty numpy arr. 
    """
    global CUMULATIVE_DATA, FEATURE_COLS
    
    CUMULATIVE_DATA = np.zeros((1,FEATURE_COLS), dtype=float, order='C') # holds rows of sensor data with 12 extracted cols
    CUMULATIVE_DATA = np.delete(CUMULATIVE_DATA, 0,axis=0)


# In[13]:


# # for testing 
# df = pd.read_csv("./capstone_data/test/dab_sean_1.csv", index_col=None, header = None )
# iv, ivshape = append(np.asarray(df.values[0:40, 0:6]))
# print("input vector shape:", ivshape)
# resetCumData()
# CUMULATIVE_DATA


# In[14]:


#iv

