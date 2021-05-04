#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   constants.py
@Time    :   2021/04/09 11:38:08
@Author  :   GE5219 Group 10
@Version :   1.0
@Contact :   xu_yuting@u.nus.edu/e063065@u.nus.edu/e0575788@u.nus.edu
@Desc    :   This script contains constant values that are used by all other scripts
'''

# %%
# import libraries
import os

# In[ ]:
# ArcGIS Online log-in credentials
agol_home_url = "https://msc2020.maps.arcgis.com"
agol_username = "e0630565_MSC2020"
agol_password = "vistacf31"

#%%
# LTA Data Mall Account Key
LTA_ACCOUNT_KEY = "QP3rLvYlQEyO/W4uVxw4Bw=="
Second_LTA_ACCOUNT_KEY = "a1kp0z47RF2pF/N7x9nKJA== "     # alternative account key should the first fails
# In[ ]:
# LTA Data Mall API Request URLs
traffic_camera_request_url = "http://datamall2.mytransport.sg/ltaodataservice/Traffic-Imagesv2" 
TAXI_AVAIL_URL = "http://datamall2.mytransport.sg/ltaodataservice/Taxi-Availability" 
traffic_speedband_request_url = "http://datamall2.mytransport.sg/ltaodataservice/TrafficSpeedBandsv2"  
Train_Service_Alert_URL = "http://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"  
Traffic_Incidents_URL = "http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"  
Bus_Stop_URL = "http://datamall2.mytransport.sg/ltaodataservice/BusStops"
Bus_Passenger_Volume_URL = "http://datamall2.mytransport.sg/ltaodataservice/PV/Bus"
Train_Passegner_Volume_URL = "http://datamall2.mytransport.sg/ltaodataservice/PV/Train"
Est_Travel_Time_URL = "http://datamall2.mytransport.sg/ltaodataservice/EstTravelTimes"  
Est_Travel_Time_Item_ID = "252a9486b58847efb018ef10447577f1" 



# In[ ]:
# ArcGIS Online feature service item IDs
traffic_camera_item_id = "d04ade5efb11495cbec67dc55673ccd7" 
TAXI_AVAIL_ITEM_ID = "788b8a87f104480f959953a70c2c081c"  
traffic_speedband_item_id = "00f7c93d0b8d4b2b8778aaa2f7664264"
Train_Service_Item_ID = "e05958b9591f47ffb6c619f6f6905d56" 
Traffic_Incidents_Item_ID = "e69244c0a3914b9da2e7db1d2cda970a" 
traffic_image_service_root ="https://services5.arcgis.com/KiRa9d9aHfdXiCqt/arcgis/rest/services/Traffic_Images/FeatureServer/0/"
Bus_Stop_Item_ID = "40f284b915c74fcfaa7416681943416c"
Passenger_Volume_Item_ID = "2bdac2248a5c4844ad73004d7873e8cf"
Last_Updated_Table_Item_ID = "d7464b20032740f0be4b3f0c240d5c80"
Expressway_Landmark_Item_ID = "8b6133ef829d4102b4642b3b7f56fa7d"


taxi_density_item_id = "a47c882797c94a3ca4a126a449dfeb51"

# %%
# folder path for downloading images and saving log files
# to be created in the same directory as the script files 
download_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tempdownload")
log_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
fgdb_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fgdb")
taxi_fgdb_name = "TaxiFGDB.gdb"

# %%
# ArcGIS Online feature service - feature templates
table_template = {'attributes': {}}
point_template = {'attributes':{},
                  'geometry': {'x':0, 
                               'y': 0, 
                               'spatialReference':{"wkid":4326,"latestWkid":4326}
                               }
                            }

line_template = {'attributes':{}, 
                'geometry': {'paths':[[]], 
                            'spatialReference':{"wkid":4326,"latestWkid":4326}
                            }
                }

polygon_template = {'attributes':{}, 
                'geometry': {'rings':[[]], 
                            'spatialReference':{"wkid":4326,"latestWkid":4326}
                            }
                }


highway_name_match = {"PIE": "Pan-Island Expressway", 
                        "SLE": "Seletar Expressway", 
                        "AYE":"Ayer Rajah Expressway",
                        "BKE": "Bukit Timah Expressway", 
                        "KJE": "Kranji Expressway",
                        "CTE": "Central Expressway",
                        "ECP": "East Coast Parkway",
                        "MCE": "Marina Coastal Expressway",
                        "TPE": "Tampines Expressway",
                        "KPE": "Kallang-Paya Lebar Expressway"}
# In[ ]:



