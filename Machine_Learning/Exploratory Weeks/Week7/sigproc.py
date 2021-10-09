#!/usr/bin/env python
# coding: utf-8

# In[28]:


import numpy as np
import scipy as sp
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt
from scipy import stats
get_ipython().run_line_magic('matplotlib', 'inline')
plt.style.use('ggplot') 
from IPython.display import display, HTML

from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn import preprocessing


# In[29]:


def loadDataFiles(folderPath):
    """Takes folderPath as a param. 
       Returns all files inside as a list.
    """
    dataFiles = sorted(glob(folderPath))
    return dataFiles


# In[30]:


def lookUp(dframe,sub,trialNum, dance):
    """Takes dataframe, subject, trialNumber and danceMove.
       Returns the dataframe under consideration.
    """
    df_considered = dframe[(dframe["subject"] == sub) & (dframe["trial"] == trialNum) & (dframe["target"] == dance)]
    return df_considered


# In[31]:


def encodeActivityName(df, activityColumnName, label):
    """Takes dframe, activityColumnName 
       and desired label for encoded activityName.
       Function adds a new column as per label to the dframe.
       No return value. 
    """
    le = preprocessing.LabelEncoder()
    df[label] = le.fit_transform(df[activityColumnName].values.ravel())
    print(le.classes_.size)
    print(list(le.classes_))
    


# In[32]:


def normaliseData(dframe, columnNames):
    """
    Takes in dframe and list of columns to be normalised. 
    Normalize features for training data set (values between 0 and 1).
    Columns rounded to 4dp after normalisation. 
    No return value
    """
    pd.options.mode.chained_assignment = None  # default='warn'
    for col in columnNames:
        dframe[col] = dframe[col] / dframe[col].max()
        dframe[col] = dframe[col].round(4)


# In[33]:


def segmentation(df,samplingFreq,window,overlap,encodedTargetColumn):
    """
    Takes df, samplingFreq, window,overlap, encodedTargetColumn,where
    samplingFreq in Hz
    window = the time interval of one window in seconds,
    overlap = num of steps to take from one segment/window to the next
    """
#     window size = nrows = Sampling freq(Hz) * window(secs)
#     if overlap = nrows, then there is no overlap bewteen segments,
#     if accx,y,z and gyrox,y,z => 6 as numOfAxis. 

    numOfAxis = 6
    segments = []
    labels = []
    nrows = samplingFreq * window
    for i in range(0, len(df) - nrows, overlap):
        ax = df["ax"].values[i:i+nrows]
        ay = df["ay"].values[i:i+nrows]
        az = df["az"].values[i:i+nrows]
        gx = df["gx"].values[i:i+nrows]
        gy = df["gy"].values[i:i+nrows]
        gz = df["gz"].values[i:i+nrows]
        
        # retrieve the most used label in this segment 
        label = stats.mode(df[encodedTargetColumn][i:i+nrows])[0][0]
        # each segment appended represents a window's values for each of 
        # the axial values
        segments.append([ax,ay,az,gx,gy,gz])
        labels.append(label)
    
    reshaped_segments = np.asarray(segments,dtype =np.float32).reshape(-1,nrows,numOfAxis)
    labels = np.asarray(labels)
    
    # reshaped_segments will be x and labels will be y 
    return reshaped_segments, labels


# In[34]:


def getInputVector(reshapedSegments, samplingFreq, window, numOfAxis):
    input_features = samplingFreq * window * numOfAxis
    inputVector = reshapedSegments.reshape(reshapedSegments.shape[0], input_features)
    return inputVector.astype("float32")
    


# In[35]:


def oneHotTarget(y_train,num_classes):
    y_train_hot = np.utils.to_categorical(y_train,num_classes)
    return y_train_hot


# In[ ]:




