#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   001_BulkExportLayerToJpg.py
@Time    :   2021/05/04 20:41:41
@Author  :   Xu Yuting
@Version :   1.0
@Contact :   xu_yuting@hotmail.com
@Desc    :   This script exports a layout from ArcGIS Pro project in bulk
'''


# get project
import arcpy
import os

jpg_export_folder = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\Result\Weighted Degree"


# In[2]:


proj_path = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\GE6211SDH.aprx"
aprx = arcpy.mp.ArcGISProject(proj_path)


# In[3]:


# get map
m = aprx.listMaps("Map1")[0]
m


# In[4]:


pr_layout = aprx.listLayouts("Layout1")[0]
hour_element = pr_layout.listElements("TEXT_ELEMENT", "HOUR")[0]
# day_type_element = pr_layout.listElements("TEXT_ELEMENT", "DAY")[0]


# In[6]:


refLyr = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\networklyr.lyrx"


# In[8]:


import time


# In[6]:


defQuery = "StartX <> 0 And StartY <> 0 And EndX <> 0 And EndY <> 0"

for hour in range(0,24):
        
    lyr_name = "Weekday {}:00".format(str(hour).zfill(2))
    
    lyr = m.listLayers(lyr_name)[0]
        #arcpy.management.ApplySymbologyFromLayer(lyr, refLyr, None, "MAINTAIN")
        #lyr.definitionQuery = defQuery
    lyr.visible = True
        
    
    hour_element.text = "{}:00".format(str(hour).zfill(2))
        #day_type_element.text = day_type_map[day_type]
    
    out_jpg = "202101_Weekday_{}.jpg".format(str(hour).zfill(2))
    out_jpg_path = os.path.join(jpg_export_folder, out_jpg)
    
    pr_layout.exportToJPEG(out_jpg_path,300)
    print(out_jpg_path)
    
    lyr.visible = False
        
   

    


# In[ ]:




