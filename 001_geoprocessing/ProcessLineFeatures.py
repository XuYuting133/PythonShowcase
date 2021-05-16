# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Process Line Features to Network
# 
# This exercise addresses specific tasks below:
# 
# - Accurate extraction of line intersections, start points and end points
#     - line intersections are defined as: points that appear as vertices in more than one line 
#     - start and end points are the first and last vertices of every line feature 
# - construct an edge table that represent connectivity between any pair of point features from the previous task 
#     - in an edge table representation, we are primarily concerned with *immediate connectivity*: when two points appear in the same line segment
#     - weight of the edge is the physical distance between the two point features
# 
# 
# The output edge table will be used to perform percolation analysis.
# %% [markdown]
# ## Extract Intersection/Start/End Points

# %%
import os, sys 
import geopandas as gpd 
import networkx as nx 
import pandas as pd 
import numpy as np 
from shapely.geometry import LineString
from shapely.geometry import Point
import matplotlib.pyplot as plt 


# %%
# import shapefile dataset 
orig_features = gpd.read_file(r"data/RoadSectionLine.shp")
orig_features.plot()


# %%
orig_features.head()


# %%
# to extract intersection points, we first gather a set of all point coordinates, and identify the duplicates among them
singlepart_features = orig_features.explode()
singlepart_features.info()


# %%
singlepart_features['PtSequence'] = singlepart_features.apply(lambda x: [y for y in x['geometry'].coords], axis=1)
singlepart_features['PtSequence'].head()


# %%
point_list = singlepart_features['PtSequence'].to_list()    # nested list of point sequences
flat_point_list = [item for sublist in point_list for item in sublist]  # flatten the list

# get duplicates - intersections
import collections
pt_intersection = [item for item, count in collections.Counter(flat_point_list).items() if count > 1]


# %%
pt_intersection[:5]


# %%
# now we'll get a list of start and end coordinates
pt_start = [pt[0] for pt in point_list]
pt_end = [pt[-1] for pt in point_list]


# %%
# merge 3 lists and keep only unique
pt_all = pt_intersection + pt_start + pt_end 
pt_all = list(set(pt_all))
len(pt_all)


# %%
# create a geodataframe and plot the points
geometry = [Point(xy) for xy in pt_all]
gdf = gpd.GeoDataFrame(geometry, columns=['geometry'])
gdf.head()


# %%
gdf.plot(markersize=1,c='k',alpha=0.5)

# %% [markdown]
# Looks quite neat. We now move on to the next task to determine connectivity between immediate pair of points

# %%
# add index and export to shapefile
gdf['ID'] = gdf.index
# gdf.to_file(r"data/RoadPoint.shp")


# %%
# generate a point coordinates:ID dictionary
pt_dict = {}
for l in pt_all:
    # trim coordinates to 6 digits
    trim_l = (round(l[0], 6), round(l[1], 6))
    pt_dict[trim_l] = pt_all.index(l)

# %% [markdown]
# ## Clean up Line Features
# %% [markdown]
# The idea is that, a point can only be connected to its immediate neighbour. Secondary connectivity is implied between non-neighbouring points.

# %%
# iterate every line feature to obtain connected segments between points in pt_all list (intersection, start/end points)

detailed_segments = []
seg_id = 0
simplified_segments = []

for segment in point_list:
    detailed_segment = []

    start_pt = segment[0]
    prev_pt = segment[0]
    detailed_segment.append(start_pt)

    for pt in segment[1:]:
        simplified_segment = (start_pt, pt)
        detailed_segment.append(pt)
        segment = (start_pt, pt)
        if pt in pt_all:
            simplified_segments.append({'SegmentID': seg_id, 'PtSequence': simplified_segment})
            detailed_segments.append({'SegmentID': seg_id, 'PtSequence': tuple(detailed_segment)})
            start_pt = pt 
            seg_id += 1
        
        prev_pt = pt
        


# %%

print(len(detailed_segments))
print(len(simplified_segments))


# %%
detailed_segments[:3]


# %%



# %%
simplified_segments[:5]


# %%



# %%
# convert both to geodataframe
simplified_gdf = gpd.GeoDataFrame(simplified_segments)
simplified_gdf['geometry'] = simplified_gdf.apply(lambda x: LineString(x['PtSequence']), axis=1)

detailed_gdf = gpd.GeoDataFrame(detailed_segments)
detailed_gdf['geometry'] = detailed_gdf.apply(lambda x: LineString(x['PtSequence']), axis=1)


# %%
detailed_gdf.head()


# %%
simplified_gdf


# %%
# plot the detailed line with simplified line together
fig, ax = plt.subplots(1, 3, figsize=(24, 10), sharey=True)
fig.subplots_adjust(wspace=0, hspace=0)
plt.tight_layout()

# detailed road segments
detailed_gdf.plot(ax=ax[0], linewidth=1)
ax[0].set_title = "Detailed Road Segments"

# simplified road segments
simplified_gdf.plot(linewidth=1, ax=ax[1])
ax[1].set_title  = "Simplified Road Segments"

# overlay point and lines
gdf.plot(markersize=1, ax=ax[2], c='r')
simplified_gdf.plot(linewidth=1, ax=ax[2], color='gray')
ax[2].set_title = "Simplified Road Segments + intersection points"

plt.show()


# %%
# zoom to one area
fig, ax = plt.subplots(1, 1, figsize=(20,15))
gdf.plot(markersize=3, ax=ax, c='r')
detailed_gdf.plot(linewidth=1, ax=ax, color='gray')
plt.xlim([25000, 30000])
plt.ylim([30000, 35000])


# %%
# zoom to one area
fig, ax = plt.subplots(1, 1, figsize=(20,15))
gdf.plot(markersize=3, ax=ax, c='r')
simplified_gdf.plot(linewidth=1, ax=ax, color='gray')
plt.xlim([25000, 30000])
plt.ylim([30000, 35000])


# %%
# export results so far to shapefile
simplified_gdf[['SegmentID', 'geometry']].to_file(r"data/RoadSegments_Simplified.shp")
detailed_gdf[['SegmentID', 'geometry']].to_file(r"data/RoadSegments_Detailed.shp")

# %% [markdown]
# ## Export to Weighted Edge Table
# 
# The last step of this exercise is to generate the edge table in the format of:
# 
# *StartPtID, EndPtID, Weight* 
# 
# where weight is represented by actual length of road segments.
# For this we will need to create an ID table of points and length of every road segment

# %%
# first we get the length of every small segment
detailed_gdf['length'] = detailed_gdf['geometry'].length


# %%
# extract start/end point
simplified_gdf['StartPtCoord'] = simplified_gdf.apply(lambda x: (round(x['geometry'].coords[0][0], 6), round(x['geometry'].coords[0][1], 6)), axis=1)
simplified_gdf['EndPtCoord'] = simplified_gdf.apply(lambda x: (round(x['geometry'].coords[1][0], 6), round(x['geometry'].coords[1][1], 6)), axis=1)
simplified_gdf['StartPtID'] = simplified_gdf.apply(lambda x: pt_dict[x['StartPtCoord']], axis=1)
simplified_gdf['EndPtID'] = simplified_gdf.apply(lambda x: pt_dict[x['EndPtCoord']], axis=1)


# %%
simplified_gdf.head()


# %%
# concartenate two df
full_line_df = simplified_gdf[['StartPtID', 'EndPtID', 'SegmentID']].join(detailed_gdf[['SegmentID', 'length']], how='inner', on="SegmentID", lsuffix='_simplified', rsuffix='_detailed')


# %%
full_line_df.head()


# %%
full_line_df.info()


# %%
# write weighted edge table to file
f = open(r"data/roadsegment.edgelist", "w")
for d in full_line_df.iterrows():
    f.write("{} {} {}\n".format(int(d[1]['StartPtID']), int(d[1]['EndPtID']), d[1]['length']))

f.close()


# %%
# import edgelist as network
g = nx.read_weighted_edgelist(r"data/roadsegment.edgelist")


# %%
len(g.nodes)


# %%
len(g.edges)


# %%
nx.number_connected_components(g)


