#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   CommonModules.py
@Time    :   2021/04/09 11:37:12
@Author  :   GE5219 Group 10
@Version :   1.0
@Contact :   xu_yuting@u.nus.edu/e0630565@u.nus.edu/e0575788@u.nus.edu
@Desc    :   This script contains functions that are used by all other scripts
'''

# import libraries/modules
import requests
import json
import time
import constants
from copy import deepcopy
from arcgis.gis import GIS
import datetime
import os
import sys

class GeometryError():

    """
     GeometryError: raised if the dataset claims to contain location info 
     but the geometry is not one of point/line/polygon

    """
    pass


def request_from_LTA(url, account_key, additional_param_pair=None, exceed_return_limit=False):
    """
    request_from_LTA sends requests via LTA Data Mall with provided parameters

    Args:
        url (str): API url
        account_key (str): LTA Data Mall API account key
        additional_param_pair (dict, optional): Dictionary of additional request parameters. Defaults to None.
        exceed_return_limit (bool, optional): Whether the dataset will have more than 500 records. Defaults to False.

    Returns:
        list: list of dictionaries of returned data
    """

    headers = {'AccountKey': account_key}       # initialise request header to include the account key

    if additional_param_pair:                   # include additional header parameters if necessary
        url += "?"
        for param in additional_param_pair.keys():         
            url += param + "=" + additional_param_pair[param] # new parameter to be added to the request URL

    skip = 0                                    # initialise $skip parameter
    all_returned_data = []                      # initialise an empty list for returned data
        
    if exceed_return_limit:                     # if the dataset is known to contain more than 500 data records
        while True:                             # iterate the request process until all data received

            response = requests.request("GET",
                                        url + "?$skip={}".format(skip),
                                        headers=headers,
                                        data={})            # send request using GET method and skip previous records
            result = response.text                          # load result from response
            result_dict = json.loads(result)                # convert json to dict
            result_data = result_dict['value']              # read only the value key from result

            if len(result_data) < 500:                      # Case 1: fewer than 500 records --> iteration reaches the end 
                all_returned_data.extend(result_data)       # add new result to list
                break                                       # exit the loop

            else:                                           # Case 2: this iteration is not the end; continue with loop
                all_returned_data.extend(result_data)       # add new result to list
                time.sleep(30)                              # accounting for request rate limit imposed by LTA
                skip += 500                                 # for the next iteration, skip this set of 500 records

    else:                                                   # if the dataset is known to have less than 500 records
        response = requests.request("GET", url, headers=headers, data={})   # perform one-time request
        result = response.text                              # load result from response
        result_dict = json.loads(result)                    # convert json to dict
        all_returned_data = result_dict['value']            # read only the value key from result

    return all_returned_data                                # return result to main function


def RemoveAndAppendNewData(feature_layer, new_dataset, data_schema, 
                           location=True, geometry="point", table=False,
                           selected_remove=None):
    """
    RemoveAndAppendNewData [This function deletes existing features in the feature service and append new features]

    Args:
        feature_layer (AGOL feature layer): feature layer item from ArcGIS Online
        new_dataset (list): list of new data to be appended (in dictionary)
        data_schema (list): list of attribute fields of data
        location (bool, optional): True/False if the data contains location 
                                    (attribute fields must be "Longitude" and "Latitude"). Defaults to True.
        geometry (str, optional): point/line - geometry type of the dataset. Defaults to "point".
        table (bool, optional): True/False if the data is a table]. Defaults to False.
        selected_remove (dict, optional): dictionary of field name and field value of existing features to be deleted

    Raises:
        GeometryError: when the dataset contains location but wrong geometry type is given

    Returns:
        add_result: result of udates
    """


    new_feature_list = []                               # initialise empty list for new features
    if selected_remove is not None:                     # only delete a subset of the features if parameter is provided
        where_clause = ""
        for attr in (selected_remove.keys()):
            where_clause += "{} = '{}'".format(attr, selected_remove[attr])
            print(where_clause)
        feature_layer.delete_features(where=where_clause)
    else:
        feature_layer.delete_features(where="1=1")      # always true - delete all features


    if geometry == "point":                             # initialise feature data template based on geometry type
        data_template = constants.point_template
    elif geometry == "line":
        data_template = constants.line_template
    elif geometry == "polygon":
        data_template = constants.polygon_template
    elif table:
        data_template = constants.table_template
    elif location:
        raise GeometryError                             # data contains location but is neither point/line, raise error
    else:
        pass

    for new_data in new_dataset:                        # iterate and format all data to expected format
        new_feature = deepcopy(data_template)           # create a copy of the data template
        for attribute in data_schema:                   # assign attributes based on schema given
            new_feature['attributes'][attribute] = new_data[attribute]
        
        if location and geometry == "point":            # point geometry: assign x/y from Longitude/Latitude keys
            try:                                        # data from LTA API: Longitude/Latitude keys
                new_feature['geometry']['x'] = float(new_data['Longitude'])
                new_feature['geometry']['y'] = float(new_data['Latitude'])
            except KeyError:                            # exception case for data from OneMap API (different keys)
                new_feature['geometry']['x'] = float(new_data['LONGITUDE'])
                new_feature['geometry']['y'] = float(new_data['LATITUDE'])
            
        elif location and geometry == "line":           # line geometry: create line parts from Location key
            line_parts = new_data['Location'].split(" ")
            i = 0
            while i < len(line_parts):                  # iterate line parts and create paths from segments
                new_feature['geometry']['paths'][0].append([float(line_parts[i+1]), float(line_parts[i])])
                i += 2
        
        elif location and geometry == "polygon":        # polygon geometry: read JSON string of geometry from PolygonGeometry key
            new_feature['geometry']['rings'] = new_data["PolygonGeometry"]
        
        elif location:                                  # data claims to contain location but is not one of point/line/polygon
            raise GeometryError                         # raise a customised GeometryError
        
        else:                                           # no location for this dataset, skip
            pass

        new_feature_list += [new_feature]               # add the new feature to the list
        del new_feature

        # if more than 6000 new features, add data in chunk size of 2000
        # if fewer than 6000 new features, no need to split up the new feature list
        if len(new_dataset) > 6000 and len(new_feature_list) % 2000 == 0:
            add_result = feature_layer.edit_features(adds=new_feature_list)     # add new features to feature service
            new_feature_list = []                                               # reset new_feature_list
            if not add_result['addResults'][0]['success']:                      # if adding new feature is not successful
                print(add_result)                                               # print error
                sys.exit()                                                      # terminate process
                
                
    add_result = feature_layer.edit_features(adds=new_feature_list)             # add the last chunk of new features to feature service
    if not add_result['addResults'][0]['success']:                              # if adding new feature is not successful
                print(add_result)                                               # print error
                sys.exit()
    return add_result                                                           # return add_result


def UpdateLastUpdatedTime(agol_connection, dataset):
    
    """
    UpdateLastUpdatedTime funtion updates the last updated time on feature service for specific datasets    

    Args:
        agol_connection (ArcGIS Online instance): an ArcGIS Online instance
        dataset (string): name of the dataset for which last updated time should be updated
    """
    
    updatedtime_service = agol_connection.content.get(constants.Last_Updated_Table_Item_ID)     # obtain the feature service for last updated timestamp
    updatedtime_layer = updatedtime_service.layers[0]                                           # read the first layer from the service
    last_updated_time = datetime.datetime.now()                                                 # get the current timestamp
    result = updatedtime_layer.delete_features(where="Dataset='{}'".format(dataset))            # delete existing record of the dataset's timesstamp
    dataset_record = deepcopy(constants.point_template)                                         # initialise a feature template
    dataset_record['attributes'] = {'Dataset': dataset,
                                    "LastUpdatedTime": last_updated_time}                       # Update dataset name and current timestamp
    result = updatedtime_layer.edit_features(adds=[dataset_record])                             # add record to feature service
    
    print(result)
    