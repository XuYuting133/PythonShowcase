#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   GetPassengerVolume.py
@Time    :   2021/04/11 20:28:52
@Author  :   GE5219 Group 10
@Version :   1.0
@Contact :   xu_yuting@u.nus.edu/e0630565@u.nus.edu/e0575788@u.nus.edu
@Desc    :   This script retrieves Passenger Volume data and updates the feature service
'''


# %%
# import libraries/packages needed
import time
starttime = time.time()
import requests
import json
import time
from arcgis.gis import GIS
import urllib.request
import os
import datetime
from zipfile import ZipFile
import constants                    # this script contains common variables used by all scripts
import CommonModules                # this module contains common functions used by all scripts
import datetime
import pandas as pd
import sys


# %%
class ModeError():
    """
    ModeError is a customized class of errors raised when the provided transport mode is neither train nor bus
    """
    pass

# %%

def UpdatePassengerVolume(transport_mode):
    """
    UpdatePassengerVolume removes and appends new paassenger volume at transit nodes data for a specified transport mode

    Args:
        mode (str): "BUS" or "TRAIN" trasport mode

    Raises:
        ModeError: raised if the transport mode falls outside of bus/train
    """
    
    Passenger_Item_ID = constants.Passenger_Volume_Item_ID                  # get the required variables from constants module
    account_key = constants.Second_LTA_ACCOUNT_KEY        
    
    try:                   
        if transport_mode.upper() == "BUS":                                 # get the corresponding API url based on transport mode
            Passenger_Volume_URL = constants.Bus_Passenger_Volume_URL 
        elif transport_mode.upper() == "TRAIN":
            Passenger_Volume_URL = constants.Train_Passegner_Volume_URL
        else:
            raise ModeError                                                 # if neither mode is received, raise ModeError
    except ModeError:                                                       # if ModeError raised, terminate the process
        print("Unexpected transport mode received. Terminate the process.")
        sys.exit()

    today_date = datetime.date.today()                                      # get today's timestamp
    if today_date.day >= 15:                                                # if today is or after the 15th, request last month's data (as per API doc)
        request_date_string = (today_date - datetime.timedelta(days=31)).strftime("%Y%m")
    else:                                                                   # if today is before the 15th, request for data from two months ago
        request_date_string = (today_date - datetime.timedelta(days=45)).strftime("%Y%m")

    new_passenger_volume_response = CommonModules.request_from_LTA(Passenger_Volume_URL, 
                                                   account_key, 
                                                   additional_param_pair={"Date": request_date_string}) # request new passenger volume data via LTA data mall
    downloaded_file = DecodeURLToFile(new_passenger_volume_response, transport_mode)                    # download and extract the file from the response received
    new_passenger_volume_data = TransformFileToDataList(downloaded_file, transport_mode)                # read and process the file received 
    agol_connection = GIS(constants.agol_home_url, 
                        constants.agol_username, 
                        constants.agol_password, 
                        verify_cert=False)                                          # connect to ArcGIS Online

    passenger_vol_layer = agol_connection.content.get(Passenger_Item_ID).tables[0]  # acquire the first table in the passenger volume feature service
    data_schema = list(new_passenger_volume_data[0].keys())                         # get the list of attribute names as schema
    update_result = CommonModules.RemoveAndAppendNewData(passenger_vol_layer, 
                                                        new_passenger_volume_data, 
                                                        data_schema, 
                                                        location=False, 
                                                        table=True, 
                                                        geometry=None,
                                                        selected_remove={"PT_TYPE": transport_mode})  # remove existing records for the specified mode and append new records

    CommonModules.UpdateLastUpdatedTime(agol_connection, "Passenger Volume of {} Transit Nodes".format(transport_mode))   # update last updated timestamp on feature service

# In[9]:
def TransformFileToDataList(csvFile,mode='BUS'):
    """
    TransformFileToDataList read the csv file of passenger volume data and transforms the data to 
    expected format of list of dictionaries, with column names matching feature service schema

    Args:
        csvFile (file): path to the downloaded passenger volume CSV file

    Returns:
        list: list of dictionaries of passenger volume at transit nodes
    """
    
    df = pd.read_csv(csvFile)                                                           # import csv file into pandas dataframe
    df_tap_in = df.drop(columns="TOTAL_TAP_OUT_VOLUME")                                 # drop column and save as a new dataframe with only Tap In data
    df_tap_in["VolumeType"] = "TapIn"                                                   # add VoluemType column and assign TapIn text
    df_tap_in.rename(columns={"TOTAL_TAP_IN_VOLUME": "PassengerVolume"},inplace=True)   # rename field to Passenger Volume
    df_tap_out = df.drop(columns="TOTAL_TAP_IN_VOLUME")                                 # drop column and save as a new dataframe with only Tap Out data
    df_tap_out["VolumeType"] = "TapOut"                                                 # add VolumeType column and assign TapOut text
    df_tap_out.rename(columns={"TOTAL_TAP_OUT_VOLUME":"PassengerVolume"},inplace=True)  # rename field to Passenger Volume
    restructured_df = pd.concat([df_tap_in, df_tap_out], axis=0)                        # concatenate two dataframes on the same columns
    if mode == 'BUS':
        restructured_df["PT_CODE"] = (restructured_df["PT_CODE"].map(str)).str.zfill(5) # transform pt_code columne from integer to string and pad 0 
    passenger_vol_data = restructured_df.to_dict("records")                             # Covert dataframe to list of dictionary to fit the common function format
    
    return passenger_vol_data                                                           # return transformed data to main


def DecodeURLToFile(response, mode):
    """
    DecodeURLToFile reads the download linke from response, download into zip file and extract zip file
    
    Args:
        response (dict): dictionary of response values from LTA Data Mall API
        mode (string): mode of transport (BUS or TRAIN)

    Returns:
        filepath: path to the csv file containing passenger volume data
    """
    
    file_url = response[0]['Link']                                                      # read the file download linke from first value in response
    download_folder = constants.download_folder                                         # get the required download folder path from constants
    if not os.path.exists(download_folder):                                             # if the folder does not exists
        os.mkdir(download_folder)                                                       # create the folder
    download_zip = os.path.join(download_folder, "{}Passenger.zip".format(mode))        # define a filepath to save the zip file
    urllib.request.urlretrieve(file_url, download_zip)                                  # retrieve zip file from URL
    with ZipFile(download_zip, "r") as zipObj:                                          # extract all content in the current directory
        result = zipObj.extractall(download_folder)
    for f in os.listdir(download_folder):                                               # get the extracted csv file from the download folder
        if f.endswith(".csv"):
            filepath = os.path.join(download_folder, f)                                 # join folder and filename to get full path
    os.remove(download_zip)                                                             # remove zip file from disk
    
    return filepath                                                                     # return csv file path to main

def main():
    
    UpdatePassengerVolume("BUS")                # update bus passenger volume data
    UpdatePassengerVolume("TRAIN")              # update train passenger volume data


if __name__ == '__main__':
    main()

print('It took', time.time()-starttime, 'seconds.')

