#!/usr/bin/env python
# coding: utf-8

# In[1]:


import plotly.graph_objects as go

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = ["A1", "A2", "B1", "B2", "C1", "C2"],
      color = "blue"
    ),
    link = dict(
      source = [0, 1, 0, 2, 3, 3], # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = [2, 3, 3, 4, 4, 5],
      value = [8, 4, 2, 8, 4, 2]
  ))])

fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
fig.show()


# In[1]:


import plotly.graph_objects as go


# In[13]:


# plot a simple sankey diagram with nested lists 
sankey = hv.Sankey([
    ['A', 'X', 5],  # 5 elements transfer from Group A to Group X
    ['A', 'Y', 7], # 7 elements transfer from Group A to Group Y
    ['A', 'Z', 6], # 6 elements transfer from Group A to Group Z
    ['B', 'X', 2], # 2 elements transfer fro Group B to Group X
    ['B', 'Y', 9], # 9 elements transfer from Group B to Group Y 
    ['B', 'Z', 4]]
)
sankey.opts(width=600, height=400)


# In[ ]:





# In[2]:


import plotly.graph_objects as go
import urllib, json

url = 'https://raw.githubusercontent.com/plotly/plotly.js/master/test/image/mocks/sankey_energy.json'
response = urllib.request.urlopen(url)
data = json.loads(response.read())

# override gray link colors with 'source' colors
opacity = 0.4
# change 'magenta' to its 'rgba' value to add opacity
data['data'][0]['node']['color'] = ['rgba(255,0,255, 0.8)' if color == "magenta" else color for color in data['data'][0]['node']['color']]
data['data'][0]['link']['color'] = [data['data'][0]['node']['color'][src].replace("0.8", str(opacity))
                                    for src in data['data'][0]['link']['source']]

fig = go.Figure(data=[go.Sankey(
    valueformat = ".0f",
    valuesuffix = "TWh",
    # Define nodes
    node = dict(
      pad = 15,
      thickness = 15,
      line = dict(color = "black", width = 0.5),
      label =  data['data'][0]['node']['label'],
      color =  data['data'][0]['node']['color']
    ),
    # Add links
    link = dict(
      source =  data['data'][0]['link']['source'],
      target =  data['data'][0]['link']['target'],
      value =  data['data'][0]['link']['value'],
      label =  data['data'][0]['link']['label'],
      color =  data['data'][0]['link']['color']
))])

fig.update_layout(title_text="Energy forecast for 2050<br>Source: Department of Energy & Climate Change, Tom Counsell via <a href='https://bost.ocks.org/mike/sankey/'>Mike Bostock</a>",
                  font_size=10)
fig.show()


# In[17]:


import pandas as pd
import numpy as np

import holoviews as hv
import plotly.graph_objects as go
import plotly.express as pex


# In[14]:


sample_dict = {'Source':['China','Japan','Japan','Germany','Germany','USA','Japan'],
               'Target':['A','A','B','D','A','C','C'],
              'Value':[10,2,5,1,2,5,10]}


# In[11]:


df = pd.DataFrame.from_dict(sample_dict)
df.head()


# In[12]:


hv.Sankey(df)


# In[3]:


hv.extension('bokeh')


# In[3]:


nz_migration = pd.read_csv("datasets/migration_nz.csv")
nz_migration.head()


# In[4]:


nz_migration = nz_migration[nz_migration["Measure"]!="Net"]
nz_migration = nz_migration[~nz_migration["Country"].isin(["Not stated", "All countries"])]
nz_migration_grouped = nz_migration.groupby(by=["Measure","Country"]).sum()[["Value"]]
nz_migration_grouped = nz_migration_grouped.reset_index()
nz_migration_grouped.head()


# In[5]:


continents = ["Asia", "Australia","Africa and the Middle East","Europe", "Americas", "Oceania"]
continent_wise_migration = nz_migration_grouped[nz_migration_grouped.Country.isin(continents)]
continent_wise_migration


# In[97]:


continent_wise_migration.info()


# In[6]:


hv.Sankey(continent_wise_migration)


# In[8]:


continent_wise_migration.info()


# In[9]:


sankey1 = hv.Sankey(continent_wise_migration, kdims=["Measure", "Country"], vdims=["Value"])

sankey1.opts(cmap='Colorblind',label_position='left',
                                 edge_color='Country', edge_line_width=0,
                                 node_alpha=1.0, node_width=40, node_sort=True,
                                 width=800, height=600, bgcolor="snow",
                                 title="Population Migration between New Zealand and Other Continents")


# # Plot a sankey diagram showing all edges source-destination

# In[20]:


node_folder = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\Processed\202101\Edge\Bus"
import os, sys, collections


# In[23]:


f_name = [f for f in os.listdir(node_folder) if "Edgelist" in f and ".csv" in f][4]
f_name


# In[53]:


df = pd.read_csv(os.path.join(node_folder, f_name), sep=" ")
df = df[df['Weight']>500]
df = df[df['Weight']<1000]


# In[42]:


df.head()


# In[54]:


df.reset_index()


# In[18]:


hv.Sankey(df)


# In[ ]:





# In[10]:


nz_migration_grouped.head()


# In[19]:


# read all bus stop info
from collections import defaultdict
import arcpy

bus_stop_dict = {}  # dictionary of bus stop ID:location name
bus_stop_location = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\GE6211SDH.gdb\BusStop"
with arcpy.da.SearchCursor(bus_stop_location, ["BUS_STOP_N", "LOC_DESC"]) as in_cursor:
    for row in in_cursor:
        bus_stop_dict[int(row[0])] = row[1]
        
del in_cursor
print(len(bus_stop_dict))


# In[3]:


# read all modularity
import os

node_folder = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\Processed\202101\Node\Bus"
node_attr_files = [f for f in os.listdir(node_folder) if "NodeAttr" in f and ".csv" in f and "WEEKDAY" in f]
len(node_attr_files)


# In[6]:


import pandas as pd
import numpy as np
from collections import defaultdict


# In[7]:


# Create a dictionary of module class and list of bus stops
file1 = node_attr_files[2]
module_class_1 = defaultdict(list)


# In[60]:


with open(os.path.join(node_folder, file1), 'r') as in_file:
    for row in in_file:
        line = row.split(",")
        if "Id" in line:
            id_index = line.index("Id")
            module_index = line.index("modularity_class")
        else:
            module_class_1[line[module_index]].append(line[id_index])

in_file.close()


# In[20]:


file2


# In[67]:


# Create a dictionary of module class and list of bus stops
file2 = node_attr_files[4]
module_class_2 = defaultdict(list)

with open(os.path.join(node_folder, file2), 'r') as in_file:
    for row in in_file:
        line = row.split(",")
        if "Id" in line:
            id_index = line.index("Id")
            module_index = line.index("modularity_class")
        else:
            module_class_2[line[module_index]].append(line[id_index])

in_file.close()


# In[13]:


module_class_2.keys()


# In[70]:


sankey_list = []
# get overlapping count in each
for class_1 in module_class_1.keys():
    for class_2 in module_class_2.keys():
        
        exist_count = len([a for a in module_class_1[class_1] if a in module_class_2[class_2]])
        sankey_list.append([class_1, class_2, exist_count])


# In[79]:


# plot a simple sankey diagram with nested lists 
sankey = hv.Sankey(sankey_list)
sankey.opts(width=1000, height=600,cmap='tab20')


# In[21]:


key_list = module_class_1.keys()
for key in key_list:
    module_class_1[key+"_1"] = module_class_1[key]
    del module_class_1[key]


# In[22]:


module_class_1.keys()


# In[26]:


hv.extension("bokeh")


# In[28]:


module_class_1['9_1'] = module_class_1['9_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1'] 


# In[29]:


del module_class_1['9_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1']


# In[49]:





# In[32]:


bus_stop_file = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\LTA Data Mall\GEOSPATIAL\BusStopLocation\BusStopLocation.csv"


# In[33]:


bus_stop_df = pd.read_csv(bus_stop_file)


# In[52]:


bus_stop_dict = bus_stop_df.to_dict(orient='index')


# In[55]:


bus_stop_name = {}
for key in bus_stop_dict.keys():
    bus_stop_name[str(bus_stop_dict[key]['Id'])] = bus_stop_dict[key]['Label']


# In[ ]:





# In[61]:


key_list = list(module_class_1.keys())
for key in key_list:
    new_key = "Weekday_10hrs_Class{}".format(key)
    module_class_1[new_key] = module_class_1[key]
    del module_class_1[key]


# In[62]:


module_class_1.keys()


# In[68]:


key_list = list(module_class_2.keys())
for key in key_list:
    new_key = "Weekday_12hrs_Class{}".format(key)
    module_class_2[new_key] = module_class_2[key]
    del module_class_2[key]


# In[69]:


module_class_2.keys()


# In[74]:


file_3 = node_attr_files[8]
module_class_3 = defaultdict(list)
print(file_3)


# In[75]:


# Create a dictionary of module class and list of bus stops


with open(os.path.join(node_folder, file_3), 'r') as in_file:
    for row in in_file:
        line = row.split(",")
        if "Id" in line:
            id_index = line.index("Id")
            module_index = line.index("modularity_class")
        else:
            module_class_3["Weekday_16hrs_Class"+line[module_index]].append(line[id_index])

in_file.close()


# In[76]:


module_class_3.keys()


# In[77]:


# get overlapping count in each
for class_2 in module_class_2.keys():
    for class_3 in module_class_3.keys():
        
        exist_count = len([a for a in module_class_2[class_2] if a in module_class_3[class_3]])
        sankey_list.append([class_2, class_3, exist_count])


# In[ ]:




