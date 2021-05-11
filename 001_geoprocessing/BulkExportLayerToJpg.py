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

jpg_export_folder = r"C:\Users\ytxu\Documents\ArcGIS\Projects\MastersThesis\export"
if not os.path.exists(jpg_export_folder):
    os.mkdir(jpg_export_folder)

# In[2]:


proj_path = r"C:\Users\ytxu\Documents\ArcGIS\Projects\MastersThesis\MastersThesis.aprx"
aprx = arcpy.mp.ArcGISProject(proj_path)
m = aprx.listMaps("Map")[0]

# In[3]:


# In[4]:


pr_layout = aprx.listLayouts("Layout")[0]
hour_element = pr_layout.listElements("TEXT_ELEMENT", "filter")[0]
# day_type_element = pr_layout.listElements("TEXT_ELEMENT", "DAY")[0]


# In[6]:


# refLyr = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\networklyr.lyrx"


# In[8]:


import time


# In[6]:


defQueryTemplate = "Shape_Length <= {}"
textBoxTemplate = "Road Segment Length <= {}"

for length in range(0, 11000, 50):
        
    lyr_name = "RoadSectionLine"
    defQuery = defQueryTemplate.format(length)
    lyr = m.listLayers(lyr_name)[0]
        #arcpy.management.ApplySymbologyFromLayer(lyr, refLyr, None, "MAINTAIN")
    lyr.definitionQuery = defQuery
    lyr.visible = True
        
    
    hour_element.text = textBoxTemplate.format(length)
        #day_type_element.text = day_type_map[day_type]
    
    out_jpg = "RoadSegmentBelow{}.jpg".format(length)
    out_jpg_path = os.path.join(jpg_export_folder, out_jpg)
    
    pr_layout.exportToJPEG(out_jpg_path,300)
    print(out_jpg_path)
    
    lyr.visible = False
        
   

    


# In[ ]:




