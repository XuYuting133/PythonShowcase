#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   GetTrafficIncidents.py
@Time    :   2021/04/09 15:56:26
@Author  :   Xu Yuting
@Version :   1.0
@Contact :   xu_yuting@u.nus.edu/e0630565@u.nus.edu/e0575788@u.nus.edu
@Desc    :   This script queries and updates traffic incidents data on dashboard
'''

import time
starttime = time.time()
import requests, json
import os, sys
from arcgis.gis import GIS
import constants
import CommonModules
import time

# In[1]:

def main():
    
    time.sleep(30)                                                  # wait for 30s to avoid exceeding rate limit
    Traffic_Incidents_URL = constants.Traffic_Incidents_URL         # get request URL from constants
    Traffic_Incidents_Item_ID = constants.Traffic_Incidents_Item_ID # get feature service ID from constants
    account_key = constants.LTA_ACCOUNT_KEY
    new_traffic_incidents_data = CommonModules.request_from_LTA(Traffic_Incidents_URL, account_key)     # request traffic incidents data via LTA api
    agol_connection = GIS(constants.agol_home_url, 
                        constants.agol_username, 
                        constants.agol_password, 
                        verify_cert=False)                          # connect to ArcGIS Online
    traffic_incidents_layer = agol_connection.content.get(Traffic_Incidents_Item_ID).layers[0]  # get first layer of the traffic incidents feature service
    data_schema = list(new_traffic_incidents_data[0].keys())        # get list of keys as attribute field names
    add_result = CommonModules.RemoveAndAppendNewData(traffic_incidents_layer,
                                                    new_traffic_incidents_data, data_schema,
                                                    location=True, geometry="point")    # remove existing traffic incidents and append new incident data

    CommonModules.UpdateLastUpdatedTime(agol_connection, "Traffic Incidents")           # update data last updated timestamp on feature service

if __name__ == '__main__':
    main()
# %%
print('It took', time.time()-starttime, 'seconds.')
