#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   GetBusStops.py
@Time    :   2021/04/11 20:01:39
@Author  :   GE5219 Group 10
@Version :   1.0
@Contact :   xu_yuting@u.nus.edu/e0630565@u.nus.edu/e0575788@u.nus.edu
@Desc    :   This script requests and updates bus stop locations
'''


# %%
# import libraries/packages needed
import time
starttime = time.time()
import requests
import json
import constants                    # this script contains common variables used by all scripts
import CommonModules                # this module contains common functions used by all scripts
import time
from arcgis.gis import GIS


def AmendBusStopCode(busstop_data):
    """
    AmendBusStopCode checks bus stop code and maintains it as 5-digit text strings

    Args:
        busstop_data (list): list of dictionaries of bus stop data
    """
    
    for busstop in busstop_data:                                    # iterate every bus stop dictionary
        busstop['BusStopCode'] = busstop['BusStopCode'].zfill(5)    # fill leading 0 to keep all bus stop code 5-digit
    
    return busstop_data


def main():
    
    time.sleep(30)                                          # wait for 30s to avoid exceeding rate limit
    Bus_Stop_URL = constants.Bus_Stop_URL                   # get request URL/ItemID from constants module
    Bus_Stop_Item_ID = constants.Bus_Stop_Item_ID  
    new_bus_stop_data = CommonModules.request_from_LTA(Bus_Stop_URL, 
                                                    constants.LTA_ACCOUNT_KEY, 
                                                    exceed_return_limit=True)
                                                    # use the account key to query taxi data
    
    new_bus_stop_data = AmendBusStopCode(new_bus_stop_data) # process bus stop data to maintain 5 digits text
    
    agol_connection = GIS(constants.agol_home_url, 
                        constants.agol_username, 
                        constants.agol_password, 
                        verify_cert=False)                  # connect to ArcGIS Online using your credentials

    bus_stop_layer = agol_connection.content.get(Bus_Stop_Item_ID).layers[0]    # get first layer from the bus stop feature service
    data_schema = list(new_bus_stop_data[0].keys())         # get the list of attribute names as schema
    update_result = CommonModules.RemoveAndAppendNewData(bus_stop_layer, 
                                                        new_bus_stop_data, 
                                                        data_schema, 
                                                        location=True, 
                                                        geometry="point")       # remvoe existing bus stops and append new bus stops

    CommonModules.UpdateLastUpdatedTime(agol_connection, "Bus Stop")            # update Data Updated Time
    print(update_result)
if __name__ == '__main__':
    main()
print('It took', time.time()-starttime, 'seconds.')
