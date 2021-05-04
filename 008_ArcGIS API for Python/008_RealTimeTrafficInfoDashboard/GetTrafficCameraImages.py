#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   GetTrafficCameraImages.py
@Time    :   2021/04/09 15:16:28
@Author  :   GE5219 Group 10
@Version :   1.0
@Contact :   xu_yuting@u.nus.edu/e0630565@u.nus.edu/e0575788@u.nus.edu
@Desc    :   This script downloads traffic camera images from LTA data mall and upload them to feature service at the camera locations
'''
import time
starttime = time.time()
import requests, json
import constants
import CommonModules
import os, sys
import arcgis
import time
from arcgis.gis import GIS
from copy import deepcopy


def main():
        
    time.sleep(30)                                                      # wait for 30s to avoid exceeding quota
    traffic_camera_request_url = constants.traffic_camera_request_url   # get request API from constants module
    traffic_camera_item_id = constants.traffic_camera_item_id           # get feature service item ID from constants module
    account_key = constants.LTA_ACCOUNT_KEY
    new_camera_data = CommonModules.request_from_LTA(traffic_camera_request_url, account_key)   # send data request via LTA Data Mall API using the URL and account key
    download_folder = constants.download_folder                                 # get the download folder path from constants module
    if not os.path.exists(download_folder):                                     # create the folder if not available
        os.mkdir(download_folder)
        
    for d in new_camera_data:                                                   # iterate the list of new camera data
        p = requests.get(d['ImageLink'])                                        # obtain the download link
        image_download = os.path.join(download_folder, 
                                    "Image_{}.jpg".format(d['CameraID']))       # create download image filename
        with open(image_download,'wb') as in_file:                              # initialize file handler to download
            in_file.write(p.content)                                            # write data to the download file
        in_file.close()                                                         # close file handler
        d['ImageFilePath'] = image_download                                     # append file path to a new key

    agol_connection = GIS(constants.agol_home_url, 
                        constants.agol_username, 
                        constants.agol_password, 
                        verify_cert=False)                                       # connect to ArcGIS Online using credentials

    traffic_camera_layer = agol_connection.content.get(traffic_camera_item_id).layers[0]    # acquire the first layer in traffic camera image feature service

    new_features = []                                                           # initialize an empty list for new traffic camera features
    for d in new_camera_data:                                                   # iterate every new traffic camera feature
        camera_feature = deepcopy(constants.point_template)                     # intialize point feature template
        camera_feature['attributes']['CameraID'] = d['CameraID']                # assign corresponding values to corresponding fields
        camera_feature['attributes']['Longitude'] = d['Longitude']
        camera_feature['attributes']['Latitude'] = d['Latitude']
        camera_feature['geometry']['x'] = d['Longitude']
        camera_feature['geometry']['y'] = d['Latitude']
        new_features.append(camera_feature)                                      # append new feature to list

    delete_result = traffic_camera_layer.delete_features(where="1=1")           # delete all existing traffic camera features
    url_root = constants.traffic_image_service_root                             # get the feature service root URL from constants

    for i,j in zip(new_features, new_camera_data):                              # iterate every pair of formatted new features and received new camera data
        add_result = traffic_camera_layer.edit_features(adds=[i])               # add the formatted new feature
        new_id = add_result['addResults'][0]['objectId']                        # obtain the objectID of the newly added feature
        attachment_result = traffic_camera_layer.attachments.add(new_id, j['ImageFilePath'])    # upload attachment to the newly added feature from local file path
        attach_id = traffic_camera_layer.attachments.get_list(oid=new_id)[0]['id']              # obtain the attachment ID of the newly uplaoded attachment
        new_feature = traffic_camera_layer.query(where="OBJECTID='{}'".format(new_id)).features[0]  # obtain the newly added feature 
        attachment_url = url_root + str(new_id) + "/attachments/" + str(attach_id)                  # format the service url path of the newly uploaded attachment
        new_feature.attributes['ImageLink'] = attachment_url                                        # assign the attribute field ImageLink to be the service url path of the attachment
        traffic_camera_layer.edit_features(updates=[new_feature])                                   # update the attribute field ImageLink in feature service
        
    for f in os.listdir(download_folder):                                       # iterate every file in the download folder
        filepath = os.path.join(download_folder, f)                             # initialize the full file path
        os.remove(filepath)                                                     # remove the image file from disk
        
    CommonModules.UpdateLastUpdatedTime(agol_connection, "Traffic Camera Images")                   # update data last updated timestamp on feature service

if __name__ == '__main__':
    main()
    
print('It took', time.time()-starttime, 'seconds.')
