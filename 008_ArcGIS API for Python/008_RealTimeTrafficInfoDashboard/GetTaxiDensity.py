#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   GetTaxiDensity.py
@Time    :   2021/04/12 20:11:53
@Author  :   GE5219 Group 10
@Version :   1.0
@Contact :   xu_yuting@u.nus.edu/e0630565@u.nus.edu/e0575788@u.nus.edu
@Desc    :   This script updates the feature layer of contour polygon of taxi density for a specific hour
'''

import time
starttime = time.time()
# %%
import arcpy
import os
import sys
import constants                    # this script contains common variables used by all scripts
import CommonModules                # this module contains common functions used by all scripts
from arcgis.gis import GIS
import datetime

# %%
class LicenseError():
    """
    LicenseError is a customised error raised when required ArcGIS Destkop licenses are not available
    """
    pass


def CheckProductAndLicense():
    
    """
    This function validates that all necessary licenses are available
    :return: True/False
    """

    try:
        if arcpy.CheckExtension("Spatial") == "Available":  # check if spatial analyst extension is available
            arcpy.CheckOutExtension("Spatial")              # check out extension if available

        else:                                               # spatial analyst extension is not available
            raise LicenseError                              # raise license error

    except LicenseError:                                    # print customized message if license error raised
        arcpy.AddMessage("Spatial Analyst license is unavailable. Terminate the process.")
        print("Spatial Analyst license is unavailable. Terminate the process.")
        sys.exit()

    except arcpy.ExecuteError:                              # if other error encountered, print execution message
        arcpy.AddMessage(arcpy.GetMessages(2))
        print(arcpy.GetMessages(2))

# %%
def PrepareWorkspace():
    
    """
    Prepare file geodatabase workspace

    Returns:
        File Geodatabase: local file gdb to keep taxi density data
        taxi_feature_class: feature class with taxi point locations
    """
       
    # define expected file paths for file gdb folder, fgdb, taxi feature class 
    fgdb_folder = constants.fgdb_folder
    fgdb_name = constants.taxi_fgdb_name
    file_gdb = os.path.join(fgdb_folder, fgdb_name)
    taxi_feature_class_name = "TaxiLocations"
    taxi_feature_class = os.path.join(file_gdb, taxi_feature_class_name)
    
    out_coordinate_system = arcpy.SpatialReference('WGS 1984')      # define output spatial reference
    
    if not os.path.exists(fgdb_folder):                             # if file gdb folder has not been created
        os.mkdir(fgdb_folder)                                       # create the folder
    if not arcpy.Exists(file_gdb):                                  # if file gdb has not been created
        arcpy.CreateFileGDB_management(fgdb_folder, fgdb_name)      # create the file gdb
    
    if not arcpy.Exists(taxi_feature_class):                        # if the taxi feature class does not exist
                                                                    # create the point feature class in WGS84 spatial reference
        arcpy.CreateFeatureclass_management(file_gdb, 
                                            taxi_feature_class_name, 
                                            "Point", 
                                            spatial_reference=out_coordinate_system)    # create a point feature class with defined coordinate system
    
    arcpy.TruncateTable_management(taxi_feature_class)              # delete existing features in the feature class
    
    return file_gdb, taxi_feature_class                             # return fgdb and feature class path to main
    
    
    # %%
def WriteTaxiDataToFeatureClass(taxi_data, feature_class):
    """
    WriteTaxiDataToFeatureClass writes LTA returned taxi data to feature class

    Args:
        taxi_data (list): list of dictionaries containing taxi locations from LTA Data MAll
        feature_class (path): feature class path to keep taxi data
    """
    
    schema = list(taxi_data[0].keys())                              # get a list of keys from taxi data dictionary
    attribute_fields = [f for f in schema 
                        if f not in ["Longitude", "Latitude"]]      # get attribute field names that are not Longitude/Latitude
    
    insertCursor = arcpy.da.InsertCursor(feature_class, attribute_fields + ["SHAPE@XY"])
                                                                    # define insert cursor to the required field and geometry field
    
    for data in taxi_data:                                          # iterate every data point
        new_row = []                                                # create empty list to hold attribute key-value pairs
        for fld in attribute_fields:                                # add attribute field value to list in same order as attribute fields
            new_row.extend(data[fld])
        new_row.extend([(data['Longitude'], data['Latitude'])])     # add geometry field value to list
        insertCursor.insertRow(tuple(new_row))                      # convert new feature to tuple and add as new row to feature class
    
    del insertCursor                                                # delete cursor
    

# %%
def GenerateTaxiDensityFeatureClass(fgdb, taxi_feature_class):
    """
    GenerateTaxiDensityFeatureClass creates kernel density contour polygons from taxi feature class

    Args:
        fgdb (file gdb): path to local file gdb to keep the contour feature class
        taxi_feature_class (feature class): path to taxi feature class

    Returns:
        list: list of contour polygons features (polygon geometry in json)
    """
    arcpy.env.overwriteOutput = True                            # allow overwriting output
    kd_raster = arcpy.sa.KernelDensity(taxi_feature_class, 
                                       "NONE", 
                                       area_unit_scale_factor="SQUARE_KILOMETERS", 
                                       out_cell_values="DENSITIES", 
                                       method="PLANAR")         # generate kernel density raster of taxi using taxi locations

    contour_feature_class = os.path.join(fgdb, "contour")       # define output contour feature class path
    if arcpy.Exists(contour_feature_class):                     # if contour feature class already exists
        arcpy.Delete_management(contour_feature_class)          # delete the feature class
    arcpy.sa.Contour(kd_raster, 
                     contour_feature_class, 
                     contour_interval=50000, 
                     base_contour=0, 
                     contour_type="CONTOUR_SHELL_UP")           # create contour feature class in intervals of 50000 (taxi/sqkm)

    arcpy.AlterField_management(contour_feature_class, 
                                "ContourMin", 
                                'Contour', 
                                'Minimum Contour')              # rename ContourMin field (default name) to Contour to match schema of feature layer
    
    contour_dataset = []                                        # define empty list of contour dataset
    with arcpy.da.SearchCursor(contour_feature_class, 
                               ["Contour", "SHAPE@JSON", "ContourMax"]) as in_cursor:     # define search cursor to read the field Contour and polygon geometry as json string
        for row in in_cursor:                                   # iterate each polygon contour feature
            contour_dataset.append({
                "Contour": row[0],
                "PolygonGeometry": eval(row[1])['rings'],
                "ContourMax": row[2]
            })                                                  # append each polygon's Contour field value and geometry json value to list
    del in_cursor                                               # delete search cursor after using
        
    return contour_dataset                                      # return list of contour polygon to main


# %%
def main():
    
    # %%
    CheckProductAndLicense()                                    # validate that desktop license and spatial analyst extension is available
    fgdb, local_feature_class = PrepareWorkspace()              # set up necessary local folder/fgdb/feature class
    
    # %%
    hour = datetime.datetime.now().hour                         # get the hour value of execution time
        
    Taxi_Request_URL = constants.TAXI_AVAIL_URL                 # get taxi request URL from constants module
    taxi_data = CommonModules.request_from_LTA(Taxi_Request_URL, 
                                               constants.LTA_ACCOUNT_KEY,
                                               exceed_return_limit=True)
                                                                # send data request via LTA data mall api and receive data
    
    # %%
    WriteTaxiDataToFeatureClass(taxi_data, local_feature_class)                     # write taxi data to local feature class
    contour_polygon_dataset = GenerateTaxiDensityFeatureClass(fgdb, 
                                                              local_feature_class)  # generate contour polygons and get list of polygon features
    agol_connection = GIS(constants.agol_home_url, 
                      constants.agol_username, 
                      constants.agol_password, 
                      verify_cert=False)                        # connect to ArcGIS Online
    
    flayer = agol_connection.content.get(constants.taxi_density_item_id).layers[hour]
                                                                # get a specific hour's feature layer 
    update_result = CommonModules.RemoveAndAppendNewData(flayer, 
                                     new_dataset=contour_polygon_dataset, 
                                     data_schema=["Contour", "ContourMax"], 
                                     location=True, 
                                     geometry="polygon")        # update the feature layer with new polygon features
                                                                # only Contour attribute field is needed
    print(update_result)
    CommonModules.UpdateLastUpdatedTime(agol_connection, "Taxi Density") # update data last upated timestamp on feature service

# %%
if __name__ == '__main__':
    main()


print('It took', time.time()-starttime, 'seconds.')

## %%
