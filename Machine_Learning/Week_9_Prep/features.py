#!/usr/bin/env python
# coding: utf-8

# In[1]:


import math
import glob
import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import itertools
import seaborn as sn
plt.style.use('ggplot')
sn.set_style("whitegrid")
get_ipython().run_line_magic('matplotlib', 'inline')

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


# NYQ = SAMPLING_FREQ / float(2) # Nyquist frequency 
CUTOFF = 0.3 
MAXFREQ = 10 

SENSOR_COLS = ["acc_X", "acc_Y", "acc_Z", "gyro_X", "gyro_Y", "gyro_Z", "yaw", "pitch", "roll"]
COLS_USED = ["acc_X", "acc_Y", "acc_Z", "gyro_X", "gyro_Y", "gyro_Z"]
ADDITIONAL_COLS = ["subject", "trialNum", "dance"]
RAW_COLS = ["acc_X", "acc_Y", "acc_Z", "gyro_X", "gyro_Y", "gyro_Z","subject", "trialNum", "dance"]

DANCE_TO_NUM_MAP = {'dab': 0, 'jamesbond': 1, 'mermaid': 2}
# NUM_TO_DANCE_MAP = {0: 'dab', 1: 'jamesbond', 2: 'mermaid'}

TRAIN_FILEPATH = "./capstone_data/train/*.csv"
TEST_FILEPATH = "./capstone_data/test/*.csv"


# In[3]:


def load_data_paths(location):
    """
    Gets file path to each csv data file.
    Input: filepath to csv files i.e. string
    Return: 1D array of filepath to each csv which contains sensor data for each trial by a subject for a dance move 
    """
    data_paths = []
    for name in glob.glob(location):
        data_paths.append(name)
    return data_paths


# In[4]:


def normaliseTrainData(dframe):
    """
    Normalize features for data set (values between 0 and 1). Columns rounded to 4dp after normalisation.
    Input: raw sensor dframe 
    No return value
    """
    
    global COLS_USED
    
    train_max = {}
    
    pd.options.mode.chained_assignment = None  # default='warn'
    for col in COLS_USED:
        train_max[col] = dframe[col].max()
        dframe[col] = dframe[col] / dframe[col].max()
        dframe[col] = dframe[col].round(4)
    return train_max


# In[5]:


def normaliseTestData(dframe, train_max):
    """
    Normalize features for data set (values between 0 and 1). Columns rounded to 4dp after normalisation.
    Input: raw sensor dframe 
    No return value
    """
    
    global COLS_USED
    
    pd.options.mode.chained_assignment = None  # default='warn'
    for col in COLS_USED:
        dframe[col] = dframe[col] / train_max[col]
        dframe[col] = dframe[col].round(4)


#  - Each filepath corresponds to a diff csv file 
#  - Each file has 20samples per sec * 60s = 1200 values & each subject does a dance move for 3 trials
#  - Hence 3600 values per subject for a dance move
#  - Thus for n dance moves, each subject has 3600 * n values
#  - With k subjects, the dataset will have k * 3600 * n values 

# In[6]:


def gen_rawData(given_filepaths):
    """
    Generate training and test dataframes from raw sensor data packaged into dict.
    Input: given_filepaths i.e. filepaths 1D array
    Return: dictionary of raw dfs, with key being {subjectName}_{dance}_{trialNum}
    """
    frames = {}
    for filepath in given_filepaths:
        _, s, subjectName, ext = filepath.split("_")
        _, _, dance = s.split("/")
        trialNum, _ = ext.split(".")
        raw_df = pd.read_csv(filepath, names=SENSOR_COLS, index_col=None)
        raw_df.dropna(inplace= True)
        raw_df.drop(["yaw","pitch","roll"], axis=1, inplace=True)
        raw_df.reset_index(drop=True,inplace=True)
        for col in raw_df.columns: 
            raw_df[col] = raw_df[col].div(100).round(6) # received sensor data was scaled by 100 
        raw_df["subject"] = subjectName
        raw_df["trialNum"] = int(trialNum)
        raw_df["dance"] = dance
        frames[f"{subjectName}_{dance}_{trialNum}"] = raw_df
    return frames 


# In[7]:


def filter_signal(signal):
    """
    Applies 3rd order median filter for each signal i.e. Each axial column in dataset.
    Input: 1D Numpy array i.e. one column
    Return: 3rd order median-filtered signal i.e 1D Numpy array
    """
    array = np.array(signal)   
    med_filtered = medfilt(array, kernel_size=3) 
    return  med_filtered  


# In[8]:


def mag_3_signals(x,y,z): 
    """
    Finding Euclidian magnitude of 3-axial signal values of each row i.e. each sample point.
    Inputs: x, y , z columns (1D Numpy arrays)
    Return: Euclidian magnitude of each 3-axial signals
    """
    return [math.sqrt((x[i]**2+y[i]**2+z[i]**2)) for i in range(len(x))]


# In[9]:


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


# In[10]:


def time_domain_feature_gen(df):
    """
    Add time domain features to df which contains normalised sensor values.
    Input : raw df i.e. concatenated complete df with all sensor values after being normalised
    Return : df with 12 cols appended from feature extraction 
    """    

    global COLS_USED
    
    # iterate through all six axial signals 
    for column in COLS_USED:
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


# In[11]:


def concatenator(raw_dic):
    """
    Concatenate raw dict along the rows to generate raw train and raw test dframes which can be sent for feature gen.
    Input: raw_dic
    Return: concatenated_df i.e. dframe 
    """
    concatenated_df = pd.concat(raw_dic.values(), axis = 0, ignore_index=True)
    return concatenated_df


# In[12]:


def segment_df(df, targetCol):
    """
    Segment df into sliding windows of values.
    Input: df i.e. concatenated mega df containing all feature cols 
           for all sample points from all trials of dance moves by all subjects 
    Input: targetCol i.e. labels col for dance moves 
    Returns: 3D Numpy Array representing Windows of values and the corresponding labels 
    """
    global FEATURE_COLS_LEN, SEGMENT_SIZE, OVERLAP, FEATURE_COLS
    
    segments = []
    labels = []
    # In each iteration, the row jumps by the overlap size
    # grab all rows of feature column values corresponding to length of segment 
    # grab corresponding mode of targetCol
    for row in range(0, len(df) - SEGMENT_SIZE, OVERLAP):
        window = []
        for col in FEATURE_COLS: 
            window.append(df[col][row:row+SEGMENT_SIZE].values)
            
        segments.append(window)
        label = stats.mode(df[targetCol][row:row+SEGMENT_SIZE])[0][0]
        labels.append(label)
        
    reshaped_segments = np.asarray(segments,dtype =np.float32).reshape(-1,SEGMENT_SIZE,FEATURE_COLS_LEN)
    labels = np.asarray(labels)
    
    # reshaped_segments will be x and labels will be y 
    return reshaped_segments, labels


# In[13]:


def getInputVector(reshapedSegments):
    """
    Get the input vector to be fed into nn.
    Input: reshapedSegments after segmentation of df 
    Return: Input vector of shape n windows * (20*1*12)
    Note: num of windows, n = (len(df) / overlap) - 1, if you take first window as w1, else it will be (len(df) / overlap) - 2
    """
    global SAMPLING_FREQ, WINDOW_SIZE, FEATURE_COLS_LEN
    
    num_of_input_features = SAMPLING_FREQ * WINDOW_SIZE * FEATURE_COLS_LEN
    inputVector = reshapedSegments.reshape(reshapedSegments.shape[0], num_of_input_features)
    
    return inputVector.astype("float32")


# In[14]:


def lookUp(dframe,sub,trialNum,dance):
    """
    Lookup a particular subject's df based on trialNum and dance in a dataframe.
    Inputs: dataframe, str(subject), str(trialNumber) and str(danceMove)
    Returns: the dataframe under consideration.
    """
    df_considered = dframe[(dframe["subject"] == sub) & (dframe["trialNum"] == trialNum) & (dframe["dance"] == dance)]
    return df_considered


# In[15]:


def gen_mapping(danceArray):
    """
    Get two dicts. One with dance mapped to number and the other with number mapped to dance.
    Input: Unique dance moves in 1d array
    Returns: ({dance: num}, {num: dance})
    """
    map_dance_to_num = {}
    map_num_to_dance = {}
    for i, move in enumerate(danceArray): 
        map_num_to_dance[i] = move
        map_dance_to_num[move] = i
    return (map_dance_to_num, map_num_to_dance)


# In[16]:


def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues):
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.grid(False)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=90)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt), horizontalalignment="center", color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


# In[17]:


# testing
raw_test_df = concatenator(gen_rawData(load_data_paths(TEST_FILEPATH)))
raw_train_df = concatenator(gen_rawData(load_data_paths(TRAIN_FILEPATH)))
train_max = normaliseTrainData(raw_train_df)
normaliseTestData(raw_test_df, train_max)
feature_test_df = time_domain_feature_gen(raw_test_df)
feature_train_df = time_domain_feature_gen(raw_train_df)
feature_train_df["target"] = feature_train_df["dance"].map(DANCE_TO_NUM_MAP)
feature_test_df = time_domain_feature_gen(raw_test_df)
feature_test_df["target"] = feature_test_df["dance"].map(DANCE_TO_NUM_MAP)
segment_train_df = feature_train_df.drop(RAW_COLS, axis = 1)
segment_test_df = feature_test_df.drop(RAW_COLS, axis=1)
train_segs, lbl_train = segment_df(segment_train_df,"target")
test_segs, lbl_test = segment_df(segment_test_df, "target")
training_X = getInputVector(train_segs)
testing_X = getInputVector(test_segs)
print("Training segments shape: ", train_segs.shape)
print("Testing segments shape: ", test_segs.shape)
print("Input Training Vector shape: ", training_X.shape)
print("Input Testing Vector shape: ", testing_X.shape)


# In[18]:


# raw_test_df["acc_X"][0:20]

