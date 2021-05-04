#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   GetEstimatedTravelTime.py
@Time    :   2021/04/09 16:12:05
@Author  :   GE5219 Group 10
@Version :   1.0
@Contact :   xu_yuting@u.nus.edu/e0630565@u.nus.edu/e0575788@u.nus.edu
@Desc    :   This script queries and updates Traffic Speed Band data on ArcGIS dashboard
'''

#%%
# import libraries/modules
import time
starttime = time.time()
import requests
import json
import sys
from arcgis.gis import GIS
import CommonModules
import constants
import time
from arcgis.geocoding import geocode    # geocoding package from ArcGIS API for Python


# %%

def main():
    
    # ----------------- this section gets and updates estimated travel time data ------------------ #
    account_key = constants.LTA_ACCOUNT_KEY                             # get variables from constants module
    Est_Travel_Time_URL = constants.Est_Travel_Time_URL
    Est_Travel_Time_Item_ID = constants.Est_Travel_Time_Item_ID
    time.sleep(30)                                                      # wait for 30s to avoid exceeding rate limit
    new_est_travel_time = CommonModules.request_from_LTA(Est_Travel_Time_URL, account_key)  # request estimated travel time data from LTA
    agol_connection = GIS(constants.agol_home_url, 
                        constants.agol_username, 
                        constants.agol_password, 
                        verify_cert=False)                              # connect to ArcGIS Online using your credentials
    
    est_travel_time_layer = agol_connection.content.get(Est_Travel_Time_Item_ID).layers[0]  # get the first layer in the estimated travel time feature service
    data_schema = list(new_est_travel_time[0].keys())                       # get list of dictionary keys as attribute fields
    update_result = CommonModules.RemoveAndAppendNewData(est_travel_time_layer, 
                                                        new_est_travel_time, 
                                                        data_schema, 
                                                        location=False, 
                                                        geometry="point")   # remove existing records in feature service and apped new record


    # -------------------- this section creates travel segments start-point features --------------------- #
    highway_location_list = [(f['Name'], f['StartPoint']) for f in new_est_travel_time]     # get a list of (expressway, location) tuple from StartPoint locations
    highway_location_list += [(f['Name'], f['EndPoint']) for f in new_est_travel_time]      # add the list of (expressway, location) tuple from EndPoint lcoations
    highway_location_list = list(set(highway_location_list))                                # remove duplicates
    highway_fullname = constants.highway_name_match                                         # get the list of dicionaary of expressway short name - long name match
    # %%
    landmark_features = []                                                                  # initialize an empty list of ladmark features
    for highway_location in highway_location_list:                                          # iterate every (expressway, location) tuple
        landmark_feature = {}                                                               # initialize an emtpy dictionary
        landmark_feature["LocationName"] = highway_location[1]                              # assign location value to LocationName field
        landmark_feature["ExpresswayName"] = highway_location[0]                            # assign expressway value to ExpresswayName field
        search_string = highway_location[0] + " " + highway_location[1]                     # create a search string for geocoding
        try:
            search_result = geocode(search_string)[0]                                       # get the geocoding result with the highest match point
        except IndexError:                                                                  # if geocoding returns no result, skip this record
            continue
        landmark_feature["Longitude"] = search_result["location"]['x']                      # assign coordinates of the geocoding result to Longitude/Latitude keys (to match to the expected format)
        landmark_feature["Latitude"] = search_result["location"]['y']
        landmark_features.append(landmark_feature)                                          # append new landmark feature to list
    # %%
    expressway_landmark_layer = agol_connection.content.get(constants.Expressway_Landmark_Item_ID).layers[0] # get the expressway landmark feature layer
    landmark_schema = list(landmark_features[0].keys())                                     # get the list of attribute fields as schema
    update_result = CommonModules.RemoveAndAppendNewData(expressway_landmark_layer,
                                                        landmark_features,
                                                        landmark_schema,
                                                        location=True,
                                                        geometry="point")                   # remove existing landmarks and append new landmarks 
    CommonModules.UpdateLastUpdatedTime(agol_connection, "Estimated Travel Time")           # update data last updated timestamp in feature service


if __name__ == '__main__':
    main()

print('It took', time.time()-starttime, 'seconds.')
