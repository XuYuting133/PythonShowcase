#-------------------------------------------------------------------------------
# Name:        modelFunctions
# Purpose:     Contains customized functions written for this MLP.
#
# Author:      Xu Yuting
#
# Created:     26/04/2020
# Copyright:   (c) ytxu 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from sklearn.model_selection import train_test_split,cross_val_score,GridSearchCV
from sklearn.linear_model import LinearRegression,LogisticRegression,Ridge,Lasso
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.preprocessing import scale,StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report,confusion_matrix,roc_curve

import pyodbc,os,sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

scriptFolder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(scriptFolder)

from ModelConfig import *
import datetime


def preprocessing(df_list):

    # use imputer configured to impute missing values
    # transform single-column array if need be
    transformed=[]
    for df in df_list:
        if df.ndim==1:
            df=df.reshape(-1,1)

        imp=preprocessingSelector.model
        df_transformed=imp.fit_transform(df)
        transformed.append(df_transformed)

    return transformed


def dropNonNumeric(df):

    # drops all the non-numeric fields
    for col in df.columns:
        if df[col].dtypes not in ['int64','float64']:
            df.drop([col],axis=1,inplace=True)
    return df

def cleanData(df):

    # clean the dataframe based on findings from EDA

    # replace negative values with 0
    df['guest_scooter'].replace([-2,-1],np.nan,inplace=True)

    # remove 0 in relative_humidity and psi
    df['psi'].replace(0,np.nan,inplace=True)
    df['relative_humidity'].replace(0,np.nan,inplace=True)

    # clean up typos in weather column #
    df['weather']=df['weather'].str.upper()
    df.loc[df['weather']=='LEAR','weather']='CLEAR'
    df.loc[df['weather']=='CLAR','weather']='CLEAR'
    df.loc[df['weather']=='CLUDY','weather']='CLOUDY'
    df.loc[df['weather']=='LOUDY','weather']='CLOUDY'
    df.loc[df['weather']=='LIHT SNOW/RAIN','weather']='LIGHT SNOW/RAIN'

    # drop duplicates
    df=df.drop_duplicates()

    # convert weather to integer
    map_weather = {'CLEAR': 1, 'CLOUDY': 2,'LIGHT SNOW/RAIN':3,'HEAVY SNOW/RAIN':4}
    df.replace({'weather': map_weather},inplace=True)

    # extract year, month, day, weekday attributes from date
    dt=df['date']
    df['date']=pd.to_datetime(dt)
    df['year']=df['date'].dt.year
    df['month']=df['date'].dt.month
    df['day']=df['date'].dt.day
    df['weekday']=df['date'].apply(lambda x: x.weekday())
    df['weekday']=df['weekday']+1

    # map month to season
    df['season']=df['month']
    df['season'].replace([3,4,5],'Spring',inplace=True)
    df['season'].replace([6,7,8],'Summer',inplace=True)
    df['season'].replace([9,10,11],'Fall',inplace=True)
    df['season'].replace([12,1,2],'Winter',inplace=True)
    df['season'].replace('Spring',1,inplace=True)
    df['season'].replace('Summer',2,inplace=True)
    df['season'].replace('Fall',3,inplace=True)
    df['season'].replace('Winter',4,inplace=True)

    return df

def printScreen(score,cv_results,cv,preprocessModel,predictionModel):

    # Print metrics
    print("\n\n********************************************************")
    print("PREPROCESSING MODEL:")
    print(type(preprocessModel).__name__+"\n")

    print("PREDICTION MODEL:")
    print(type(predictionModel).__name__+"\n")

    print("ACCURACY SCORE ({} test data):".format(splitRatioConfig.test_data_ratio))
    print(str(score)+"\n")

    print("CROSS VALIDATION SCORE ({} fold):".format(cv))
    print(str(cv_results)+"\n")

    print("********************************************************\n\n")

def writeToText(acc_score,cv_score,cv,preprocessModel,predictorModel):

    # write metrics to txt file
    currFolder = os.path.dirname(os.path.realpath(__file__))
    folderName = OutputConfig.folderName
    outputFolder = os.path.join(currFolder,folderName)

    if not os.path.isdir(outputFolder):
        os.mkdir(outputFolder)

    postfix=datetime.datetime.now().strftime("%Y%m%d%H%M")
    fileName=OutputConfig.logFilePrefix.format(postfix)
    logFilePath=os.path.join(outputFolder,fileName)
    logFile=open(logFilePath,'a')
    logFile.write("\n********************************\n")

    logFile.write("PREPROCESSING MODEL:\n")
    logFile.write(type(preprocessModel).__name__+"\n\n")

    logFile.write("PREDICTION MODEL:\n")
    logFile.write(type(predictorModel).__name__+"\n\n")

    logFile.write("ACCURACY SCORE ({} test data):\n".format(splitRatioConfig.test_data_ratio))
    logFile.write(str(acc_score)+str("\n\n"))

    logFile.write("CROSS VALIDATION SCORE ({} fold):\n".format(cv))
    logFile.write(str(cv_score)+"\n\n")
    logFile.write("********************************\n")

    logFile.close()
    return fileName

def getTrainTestSplitRatio():
    test_size=splitRatioConfig.test_data_ratio
    random_state=splitRatioConfig.random_state
    return test_size, random_state