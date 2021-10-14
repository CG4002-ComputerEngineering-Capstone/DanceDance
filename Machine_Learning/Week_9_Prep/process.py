#!/usr/bin/env python
# coding: utf-8

# In[1]:


import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import seaborn as sn
from scipy.signal import medfilt
from scipy import stats
plt.style.use('ggplot')
sn.set_style("whitegrid")
get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


SAMPLING_FREQ = 20 # Hz 
WINDOW_SIZE = 2 # sec 
OVERLAP = 20 # 
SEGMENT_SIZE = SAMPLING_FREQ * WINDOW_SIZE # 40

SENSOR_COLS = ["acc_X", "acc_Y", "acc_Z", "gyro_X", "gyro_Y", "gyro_Z", "yaw", "pitch", "roll"]

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
    Normalize features for data set (values between -1 and 1). Columns rounded to 4dp after normalisation.
    Input: raw sensor dframe 
    Return: training set max values for each col packaged in a dict 
    """
    
    global SENSOR_COLS
    
    train_max = {}
    
    pd.options.mode.chained_assignment = None  # default='warn'
    for col in SENSOR_COLS:
        dframe[col] = dframe[col].div(100).round(6)
        train_max[col] = dframe[col].max()
        dframe[col] = dframe[col] / dframe[col].max()
        dframe[col] = dframe[col].round(4)
    return train_max


# In[5]:


def normaliseTestData(dframe, train_max):
    """
    Normalize features for data set (values between -1 and 1). Columns rounded to 4dp after normalisation.
    Input: raw sensor dframe 
    No return value
    """
    
    global SENSOR_COLS
    
    pd.options.mode.chained_assignment = None  # default='warn'
    for col in SENSOR_COLS:
        dframe[col] = dframe[col].div(100).round(6)
        dframe[col] = dframe[col] / train_max[col]
        dframe[col] = dframe[col].round(4)


# In[6]:


def filter_signal(df):
    """
    Applies 3rd order median filter for each signal i.e. Each axial column in dataset.
    Input: raw_df
    """
    global SENSOR_COLS
    
    for col in SENSOR_COLS: 
        array = np.array(df[col]) 
        med_filtered = medfilt(array, kernel_size=3) 
        df[col] = med_filtered  


# In[7]:


def concatenator(raw_dic):
    """
    Concatenate raw dict along the rows to generate raw train and raw test dframes.
    Input: raw_dic
    Return: concatenated_df i.e. dframe 
    """
    concatenated_df = pd.concat(raw_dic.values(), axis = 0, ignore_index=True)
    return concatenated_df


# In[8]:


def gen_rawData(given_filepaths):
    """
    Generate training and test dataframes from raw sensor data packaged into dict.
    Input: given_filepaths i.e. filepaths 1D array
    Return: dictionary of raw dfs, with key being {subjectName}_{dance}_{trialNum}
    """
    global SENSOR_COLS
    frames = {}
    for filepath in given_filepaths:
        _, s, subjectName, ext = filepath.split("_")
        _, _, dance = s.split("/")
        trialNum, _ = ext.split(".")
        raw_df = pd.read_csv(filepath, names=SENSOR_COLS, index_col=None)
        raw_df.dropna(inplace= True)
        raw_df.reset_index(drop=True,inplace=True)
        raw_df["subject"] = subjectName
        raw_df["trialNum"] = int(trialNum)
        raw_df["dance"] = dance
        frames[f"{subjectName}_{dance}_{trialNum}"] = raw_df
    return frames 


# In[9]:


def segment_df(df, targetCol):
    """
    Segment df into sliding windows of values.
    Input: df i.e. concatenated mega df 
    Input: targetCol i.e. labels col for dance moves 
    Returns: 3D Numpy Array representing Windows of values and the corresponding labels 
    """
    global SENSOR_COLS, SEGMENT_SIZE, OVERLAP
    
    segments = []
    labels = []
    # In each iteration, the row jumps by the overlap size
    # grab all rows of feature column values corresponding to length of segment 
    # grab corresponding mode of targetCol
    for row in range(0, len(df) - SEGMENT_SIZE, OVERLAP):
        window = []
        for col in SENSOR_COLS: 
            window.append(df[col][row:row+SEGMENT_SIZE].values)
            
        segments.append(window)
        label = stats.mode(df[targetCol][row:row+SEGMENT_SIZE])[0][0]
        labels.append(label)
        
    reshaped_segments = np.asarray(segments,dtype =np.float32).reshape(-1,SEGMENT_SIZE,len(SENSOR_COLS))
    labels = np.asarray(labels)
    
    # reshaped_segments will be x and labels will be y 
    return reshaped_segments, labels


# In[10]:


def getInputVector(reshapedSegments):
    """
    Get the input vector to be fed into nn.
    Input: reshapedSegments after segmentation of df 
    Return: Input vector of shape n windows * (20*1*12)
    Note: num of windows, n = (len(df) / overlap) - 1, if you take first window as w1, else it will be (len(df) / overlap) - 2
    """
    global SAMPLING_FREQ, WINDOW_SIZE, SENSOR_COLS
    
    num_of_input_features = SAMPLING_FREQ * WINDOW_SIZE * len(SENSOR_COLS)
    inputVector = reshapedSegments.reshape(reshapedSegments.shape[0], num_of_input_features)
    
    return inputVector.astype("float32")


# In[11]:


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


# In[12]:


raw_train_df = concatenator(gen_rawData(load_data_paths(TRAIN_FILEPATH)))
raw_test_df = concatenator(gen_rawData(load_data_paths(TEST_FILEPATH)))
filter_signal(raw_train_df)
filter_signal(raw_test_df)
TRAIN_MAX = normaliseTrainData(raw_train_df)
normaliseTestData(raw_test_df, TRAIN_MAX)
raw_test_df["target"] = raw_test_df["dance"].map(DANCE_TO_NUM_MAP)
raw_train_df["target"] = raw_train_df["dance"].map(DANCE_TO_NUM_MAP)
test_segs, lbl_test = segment_df(raw_test_df, "target")
train_segs, lbl_train = segment_df(raw_train_df, "target")
training_X = getInputVector(train_segs)
testing_X = getInputVector(test_segs)


# In[13]:


print("TrainingVector shape", training_X.shape)
print("Label Train shape", lbl_train.shape )


# In[14]:


print("TestingVector shape", testing_X.shape)
print("Label Test shape", lbl_test.shape )


# In[15]:


TRAIN_MAX

