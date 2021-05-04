#-------------------------------------------------------------------------------
# Name:        ModelConfig.py
# Purpose:     This module allows users to adjust the configurable parameters to the MLP
#
# Author:      Xu Yuting
#
# Created:     25/04/2020
# Copyright:   (c) ytxu 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from sklearn.model_selection import train_test_split,cross_val_score,GridSearchCV
from sklearn.linear_model import LinearRegression,LogisticRegression,Ridge,Lasso
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.preprocessing import scale,StandardScaler,OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report,confusion_matrix,roc_curve
import numpy as np

class crossValConfig(object):
    cv=50 # number of folds for cross validation

class OutputConfig(object):
    folderName = "metrics" # folder name where the metrics file will be saved
    logFilePrefix = "ModelMatrix_{}.txt" # file name

class predictorSelector(object):
    model=LinearRegression() # model chosen for prediction

class preprocessingSelector(object):
    model=SimpleImputer(missing_values=np.nan,strategy='most_frequent') # model set up for preprocessing
    # strategy to choose from 'mean','median','most_frequent', and 'constant' --> to be followed with a fill_value

class splitRatioConfig(object):
    test_data_ratio=0.1 # percentage of the dataset to be set aside as test data
    random_state=120 # seed used by random number generator