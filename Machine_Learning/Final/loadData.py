#!/usr/bin/env python
# coding: utf-8

# In[14]:


import pandas as pd
import glob
import numpy as np


# In[2]:


TRAIN_FILEPATH = "../capstone_data/train4/*.csv"
TEST_FILEPATH = "../capstone_data/test4/*.csv"

SENSOR_COLS = ["ax", "ay", "az", "y", "p", "r", "start_move", "checksum"]

DANCE_TO_NUM_MAP = {'dab': 0, 'jamesbond': 1, 'mermaid': 2, 
                    'scarecrow': 3, 'pushback': 4, 'cowboy': 5, 
                    'window360': 6, 'snake': 7, 'logout2': 8}


# In[3]:


def load_data_paths(location):
    """
    Gets file path to each csv data file packaged into an array.
    Input: filepath to csv files i.e. string
    Return: 1D array of filepaths to each csv 
    """
    data_paths = []
    for name in glob.glob(location):
        data_paths.append(name)
    return data_paths


# In[4]:


def gen_rawData(given_filepaths):
    """
    Data from each csv packaged into a dict. Ensure that filenames are like "dab_sean_1.csv"
    Input: given_filepaths i.e. filepaths 1D array
    Return: dictionary of raw dfs, with key being {subjectName}_{dance}_{trialNum}
    """
    global SENSOR_COLS
    
    frames = {}
    for filepath in given_filepaths:
        _, s, subjectName, ext = filepath.split("_")
        _, _, dance = s.split("/")
        trialNum, _ = ext.split(".")
        raw_df = pd.read_csv(filepath, names=SENSOR_COLS, header=None, index_col=None)
        raw_df.dropna(inplace= True)
        raw_df.drop(columns=["y", "start_move", "checksum"], axis=1,inplace=True)
        raw_df.reset_index(drop=True,inplace=True)
        raw_df["subject"] = subjectName
        raw_df["trialNum"] = int(trialNum)
        raw_df["dance"] = dance
        frames[f"{subjectName}_{dance}_{trialNum}"] = raw_df
        
    return frames 


# In[5]:


def concatenator(raw_dic):
    """
    Concatenate raw dict along the rows to generate a concatenated df.
    Input: raw_dic
    Return: concatenated_df i.e. dframe 
    """
    concatenated_df = pd.concat(raw_dic.values(), axis = 0, ignore_index=True)
    return concatenated_df


# In[6]:


def getTrainAndTestData():
    """
    Map the dance moves to target and get the full training & test data frames.
    """
    
    global TRAIN_FILEPATH, TEST_FILEPATH, DANCE_TO_NUM_MAP
    
    raw_train_df = concatenator(gen_rawData(load_data_paths(TRAIN_FILEPATH)))
    raw_test_df = concatenator(gen_rawData(load_data_paths(TEST_FILEPATH)))
    raw_train_df["target"] = raw_train_df["dance"].map(DANCE_TO_NUM_MAP)
    raw_test_df["target"] = raw_test_df["dance"].map(DANCE_TO_NUM_MAP)
    
    
    return raw_train_df, raw_test_df


# In[7]:


raw_train_df, raw_test_df = getTrainAndTestData()


# In[8]:


raw_train_df.describe()


# In[9]:


raw_test_df.describe()


# In[20]:


raw_test_df["dance"].unique()


# In[11]:


# raw_train_df

