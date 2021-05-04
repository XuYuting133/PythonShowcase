#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   GetTaxiAvailability.py
@Time    :   2021/04/09 11:38:18
@Author  :   GE5219 Group 10
@Version :   1.0
@Contact :   xu_yuting@u.nus.edu/e0630565@u.nus.edu/e0575788@u.nus.edu
@Desc    :   Acquire available taxi location from LTA and populate AGOL feature service
'''

# %%
# import libraries/packages needed
import time
starttime = time.time()
import requests
import json
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import constants                    # this script contains common variables used by all scripts
import CommonModules                # this module contains common functions used by all scripts
import time
from arcgis.gis import GIS

# %%

def main():

    time.sleep(30)                                              # wait for 30s to avoid exceeding call limit
    TAXI_AVAIL_URL = constants.TAXI_AVAIL_URL                   # get the necessary variables from constants
    TAXI_AVAIL_ITEM_ID = constants.TAXI_AVAIL_ITEM_ID  
    new_taxi_data = CommonModules.request_from_LTA(TAXI_AVAIL_URL, 
                                                constants.LTA_ACCOUNT_KEY, 
                                                exceed_return_limit=True)   # use the account key to query taxi data; dataset contains more than 500 records
    
    agol_connection = GIS(constants.agol_home_url, 
                        constants.agol_username, 
                        constants.agol_password, 
                        verify_cert=False)                                                  # connect to ArcGIS Online using credentials

    taxi_availability_layer = agol_connection.content.get(TAXI_AVAIL_ITEM_ID).layers[0]     # acquire the feature service for traffic incidents
    data_schema = list(new_taxi_data[0].keys())                                             # get the list of keys as attribute field schema
    update_result = CommonModules.RemoveAndAppendNewData(taxi_availability_layer, 
                                                         new_taxi_data,    
                                                        data_schema, location=True, 
                                                        geometry="point")                   # remove existing taxi features and append new taxi features

    CommonModules.UpdateLastUpdatedTime(agol_connection, "Taxi")                            # update dataset last updated timestamp on feature service

if __name__ == '__main__':
    main()
print('It took', time.time()-starttime, 'seconds.')
