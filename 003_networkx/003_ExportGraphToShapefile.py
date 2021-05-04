#!/usr/bin/env python
# coding: utf-8

# In[13]:


import os
import networkx as nx
import arcpy


# In[15]:


import pandas as pd


# In[14]:


input_data_folder = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\Processed\202101\Edge\Bus"
file_list = os.listdir(input_data_folder)
edgelist_list = [f for f in file_list if "Edgelist" in f and  ".csv" in f]

if not arcpy.Exists(out_fgdb):
    arcpy.CreateFileGDB_management(r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH", "NetworkGeometry.gdb")


len(edgelist_list)


# In[26]:


# store a list of dictionary of source/target location
bus_stop_dict = {}
bus_stop_location = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\GE6211SDH.gdb\BusStop"
with arcpy.da.SearchCursor(bus_stop_location, ["BUS_STOP_N", "SHAPE@XY"]) as in_cursor:
    for row in in_cursor:
        bus_stop_dict[int(row[0])] = row[1]
        
del in_cursor
print(len(bus_stop_dict))


# In[56]:


edgelist_list


# In[58]:


# READ EDGE LIST CSV AND EXPORT TO XY-LINE FORMAT
out_fgdb = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\NetworkGeometry.gdb"
arcpy.env.workspace = out_fgdb
arcpy.env.overwriteOutput = True
bus_data = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\GE6211SDH.gdb\BusStop_SVY"
spatial_ref = arcpy.Describe(bus_data).spatialReference

for f in edgelist_list:

    in_file = os.path.join(input_data_folder, f)
    day_type = f.split("_")[2]
    day_hour = f.replace(".csv","").split("_")[-1]
    out_name = "XYLine_" + day_type + "_" + day_hour    
    
    if day_type == 'WEEKDAY' and day_hour in ['0','1','10','11','12','13','14','15','16',
                                              '17','18','19','20','21','22','23','3','4','5']:
        
        continue
    elif day_hour in ['6'] and day_type=='WEEKDAY':
        df = pd.read_csv(in_file, sep=',')
    else:
        df = pd.read_csv(in_file, sep=' ')

    
    df['StartX'] = df.Source.map(lambda x: bus_stop_dict[x][0] if x in bus_stop_dict.keys() else 0)
    df['StartY']= df.Source.map(lambda x: bus_stop_dict[x][1] if x in bus_stop_dict.keys() else 0)
    df['EndX']= df.Target.map(lambda x: bus_stop_dict[x][0] if x in bus_stop_dict.keys() else 0)
    df['EndY']= df.Target.map(lambda x: bus_stop_dict[x][1] if x in bus_stop_dict.keys() else 0)
    
    out_excel = os.path.join(out_folder, out_name + ".xlsx")
    df.to_excel(out_excel)
    out_table = os.path.join(out_fgdb, out_name)
    out_FCname = "NetworkLine_" + day_type + "_" + day_hour
    out_fc = os.path.join(out_fgdb, out_FCname)
    
    arcpy.ExcelToTable_conversion(out_excel, out_table, "Sheet1")
    arcpy.XYToLine_management(out_table, out_fc, 
                              "StartX", "StartY", "EndX", "EndY", "GEODESIC", "COL_A", spatial_ref, "ATTRIBUTES")
    print(out_fc)
    


# In[35]:





# In[37]:





# In[42]:





# In[41]:


out_folder = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\Processed\202101\Shapefile\Bus"


# In[40]:


type(df)


# In[ ]:





# In[ ]:




