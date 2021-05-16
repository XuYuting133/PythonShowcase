# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Exploratory Analysis of Tweets in Singapore 
# 
# Some of the tweets acquired were already collected in Sept/Oct 2020 and written into text file. Here we perform exploratory data analysis on one day's tweets in Singapore collected.

# %%
import geopandas
import pandas as pd 
import os, sys
import matplotlib.pyplot as plt 
import seaborn as sns


# %%
import numpy as np 


# %%
tweet_file = r"C:\Users\ytxu\Documents\GitHub\PythonShowcase\002_twitter\data\tweets.txt"
tweet_df = pd.read_csv(tweet_file, sep="|",error_bad_lines=False)   # ignore error records


# %%
tweet_df.head()


# %%
tweet_df.info()


# %%
tweet_df[['Longitude', 'Latitude']].head()


# %%
# evaluate tweet location
count_with_coordinates = len(tweet_df[tweet_df['GeocodeType']=='coordinates'])
count_with_coordinates


# %%
tweet_df['Tweet_Coordinates_Type'].value_counts()


# %%
tweets_wo_coordinates = tweet_df[tweet_df['Longitude']=='None']
tweets_wo_coordinates['Place_Type'].value_counts()

# %% [markdown]
# User_location is ignored because it does not represent the actual location where the tweet is posted. From above we can generally classify tweet locations into a few types:
# - with exact coordinates: Longitude/Latitude will be specific values - only 407 tweets out of 180k tweets are precisely geocoded this way;
# - Without coordinates but described by some location names in a range of specificity - this gives another 4-5k tweets 
# - No geotag at the attribute level. These tweets may possibly reveal location info within the text. We will not go into the details here.

# %%
# create a new column to represent this
tweet_df['GeocodeType'] = tweet_df['Place_Type']
t_index = tweet_df[tweet_df['Longitude']!='None'].index
tweet_df.loc[t_index, 'GeocodeType'] = 'coordinates'
tweet_df['GeocodeType'].value_counts()


# %%
# create a chart of the language classes
ax=sns.countplot(x="GeocodeType", data=tweet_df, palette="Set2")
ax.set_yscale("log")
ax.set_title("Number of Tweets By Location Type")
ax.legend()
ax.set_xlabel("Locaton Type")
ax.set_ylabel("Number of Tweets")


# %%
from shapely.geometry import Point


# %%
def create_geom(x):

    coord = Point((float(x['Longitude']), float(x['Latitude'])))
    return coord


# %%
# filter only those with coordinates and create geometry column
tweet_w_coords = tweet_df.loc[(tweet_df['Longitude']!='None') & (tweet_df['Latitude']!='None')]
tweet_w_coords = tweet_w_coords.dropna(how='any', subset=['Longitude','Latitude'])
# tweet_w_coords['geometry'] = tweet_w_coords.apply(lambda x: create_geom(x), axis=1)


# %%
tweet_w_coords[['Longitude','Latitude', 'geometry']].head()


# %%
gdf = geopandas.GeoDataFrame(
    tweet_w_coords, geometry=geopandas.points_from_xy(tweet_w_coords.Longitude, tweet_w_coords.Latitude))


# %%
import contextily as ctx
import folium


# %%
map = folium.Map(location = [1.3900, 103.85], tiles='OpenStreetMap' , zoom_start = 11)
map


# %%
from folium.plugins import MarkerCluster


# %%
map = folium.Map(location = [1.3900, 103.85], tiles='CartoDB dark_matter' , zoom_start = 11)

geo_df_list = [[point.xy[1][0], point.xy[0][0]] for point in gdf.geometry ]

i = 0
marker_cluster = folium.plugins.MarkerCluster().add_to(map)
for coordinates in geo_df_list:

    #now place the markers with the popup labels and data
    
    popup ="<strong>User: </strong>" + str(gdf.iloc[i]['User_Screen_Name']) + '<br>' +           "<strong>Time: </strong>" + str(gdf.iloc[i]['Created_At']) + '<br>' +            "<strong>Location: </strong>" + str(gdf.iloc[i]['Place_Full_Name']) + '<br>' +             "<strong>Tweet: </strong>" + str(gdf.iloc[i]['Text']) + '<br>'
    folium.Marker(coordinates, popup=popup).add_to(marker_cluster)
    i = i + 1

map

# %% [markdown]
# 

# %%
# a closer look
map

# %% [markdown]
# 

# %%
# heat map will be a good representative of density
from folium import plugins

map2 = folium.Map(location = [1.3900, 103.85], tiles='Cartodb dark_matter', zoom_start = 11)
heat_data = [[point.xy[1][0], point.xy[0][0]] for point in gdf.geometry ]
plugins.HeatMap(heat_data).add_to(map2)
map2


# %%



