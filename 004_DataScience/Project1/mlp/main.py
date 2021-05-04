#-------------------------------------------------------------------------------
# Name:        main
# Purpose:     Main executing script for the Machine Learning Pipeline
#
# Author:      ytxu
#
# Created:     23/04/2020
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
from sklearn.compose import ColumnTransformer

import pyodbc,os,sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

scriptFolder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(scriptFolder)

from ModelConfig import *
from modelFunctions import *
import datetime
import getInputData


def main():

    print("Process starts： "+str(datetime.datetime.now())+"\n")

    # Step 1. Get input data as dataframe
    print("Importing dataset...")
    df=getInputData.run()

    # Step 2. Data cleaning based on EDA findings
    print("Cleaning dataset...")
    df_cleaned=cleanData(df)
    df_numeric=dropNonNumeric(df_cleaned)

    # Step 3. Split dataframe to features and target
    print("Splitting dependent variable and independent variables...")
    target_col="guest_scooter"
    X=df_numeric.drop([target_col],axis=1).values
    y=df_numeric[target_col].values

    # Step 4. Split dataset to test/train data
    print("Splitting train/test dataset...")
    test_size, random_state=getTrainTestSplitRatio()
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=test_size,random_state=random_state)

    # Step 5. Imputing missing values
    print("Imputing missing data...")
    preprocessModel=preprocessingSelector.model
    [X_pp,y_pp,X_train_pp,X_test_pp,y_train_pp,y_test_pp]=preprocessing([X,y,X_train,X_test,y_train,y_test])

    # Step 6. Generate prediction using train/test datasets
    print("Building prediction pipeline...")
    predictionModel=predictorSelector.model
    steps = [('model',predictionModel)]
    pipe = Pipeline(steps)
    pipe.fit(X_train_pp,y_train_pp)
    y_pred=pipe.predict(X_test_pp)

    # Step 7. Evaluate model
    print("Evaluating model...")
    cv=crossValConfig.cv
    cv_results=cross_val_score(pipe,X_pp,y_pp,cv=cv)
    score=pipe.score(X_test_pp,y_test_pp)
    printScreen(score,cv_results,cv,preprocessModel,predictionModel)

    # Step 8.(Optional): write to text file
    writeTxtInput=input("Write metrics to text file? Yes/No:   ")
    if writeTxtInput.strip().upper()=='YES':
        fileName=writeToText(score,cv_results,cv,preprocessModel,predictionModel)
        print("Metrics written to {}".format(fileName))

    print("\nProcess ends: "+str(datetime.datetime.now()))
if __name__ == "__main__":
    main()