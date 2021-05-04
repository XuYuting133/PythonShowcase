#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   GetTrafficSpeedBand.py
@Time    :   2021/04/09 16:13:12
@Author  :   GE5219 Group 10
@Version :   1.0
@Contact :   xu_yuting@u.nus.edu/e0630565@u.nus.edu/e0575788@u.nus.edu
@Desc    :   This script queries and updates Traffic Speed Band data on ArcGIS dashboard
'''
import time
starttime = time.time()
import requests, os, sys, json
import arcgis
import constants, CommonModules
from arcgis.gis import GIS

def main():
        
    traffic_speedband_request_url = constants.traffic_speedband_request_url             # get required variables from constants
    traffic_speedband_item_id = constants.traffic_speedband_item_id
    account_key = constants.LTA_ACCOUNT_KEY
    new_traffic_speedband_data = CommonModules.request_from_LTA(traffic_speedband_request_url, 
                                                                account_key, 
                                                                exceed_return_limit=True)  # request for latest speed band data from LTA; data size known to be more than 500

    agol_connection = GIS(constants.agol_home_url, 
                        constants.agol_username, 
                        constants.agol_password, 
                        verify_cert=False)                                      # connect to ArcGIS Online using credentials

    traffic_speedband_lyr = agol_connection.content.get(traffic_speedband_item_id).layers[0]    # get the first layer in the traffic speed band feature service
    data_schema = list(new_traffic_speedband_data[0].keys())                    # get the list of keys as attribute field schema
    add_result = CommonModules.RemoveAndAppendNewData(
                                        traffic_speedband_lyr,
                                        new_traffic_speedband_data,
                                        data_schema,
                                        location=True,
                                        geometry="line")                        # remove existing speed band data and append new data
    print(add_result)
    CommonModules.UpdateLastUpdatedTime(agol_connection, "Traffic Speed Bands") # update data last upated timestamp on feature service


if __name__ == '__main__':
    main()

print('It took', time.time()-starttime, 'seconds.')
