# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Spatial Interaction Model 
# 
# The methodology of this exercise follows that of pysal documentation: http://dx.doi.org/10.18335/region.v3i2.175. The package has since evolved and continuously improved, including the structure of its modules, but the key methods remain the same.
# 
# Pysal presents four types of Spatial Interaction Models from Wilson (1971), namely:
# 1. Unconstrained
# 2. Production-constrained
# 3. Attraction-constrained 
# 4. Doubly-constrained 
# 
# In addition to a global model, pysal allows you to build local models that are calibrated at individual origins/destinations. 
# 
# Here I apply a global model on bus OD data in Singapore. The bus OD data is a small subset of bus trip data available via LTA Data Mall: https://datamall.lta.gov.sg/content/datamall/en.html. Preprocessing has been performed by matching O/D to bus stop locations, and line features connecting each pair of OD are created. Weight column carries the expected volume of passengers on the pair of OD nodes.
# 
# %% [markdown]
# ## Global Model

# %%
import geopandas as gpd 
import networkx as nx 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import os, sys 


# %%
from shapely import speedups
speedups.disable()


# %%
# import line shapefile (representing OD flows between each pair of bus stops)
orig_flow = gpd.read_file(r"data\SampleODFlow.shp")
orig_flow.head()


# %%
orig_flow.info()


# %%
orig_flow.plot(linewidth=0.5, alpha=0.01)

# %% [markdown]
# Some of the nodes are in erroneous locations (X/Y of 0,0). We will remove these OD links from the dataset.

# %%
# drop any flows that start/end at 0 (error records)
clean_flow = orig_flow[(orig_flow['StartX']!=0) & (orig_flow['StartY']!=0) & (orig_flow['EndX']!=0) & (orig_flow['EndY']!=0)]


# %%
clean_flow.info()


# %%
# normalize the link weight
minX = np.min(clean_flow['Weight'])
rangeX = np.max(clean_flow['Weight']) - minX
clean_flow['NormalizedWeight'] = clean_flow.apply(lambda x: (x['Weight']-minX)/rangeX, axis=1)
clean_flow.sort_values('NormalizedWeight', ascending=False).head()


# %%
country = gpd.read_file(r"data/SG_Boundary.shp")


# %%
# plot both weighted and unweighted OD links
fig, ax = plt.subplots(1, 2, figsize=(15, 6), sharey=True)
country.boundary.plot(linewidth=1, color='gray', ax=ax[0])
clean_flow.plot(linewidth=0.5, alpha=0.005, color='k', ax=ax[0])
country.boundary.plot(linewidth=1, color='gray', ax=ax[1])
clean_flow.plot(linewidth=clean_flow['NormalizedWeight'], cmap="Greys", ax=ax[1])

ax[0].set_title("Unweighted Links")
ax[1].set_title("Weighted Links")
plt.show()

# %% [markdown]
# After removing erroneous OD links, now all the flows are somewhat contained within the national boundary.

# %%



# %%
# sum the total flow volume by origin/destination
Sum_By_Source = clean_flow.groupby('Source').agg({'Weight': 'sum'})
sum_by_source_dict = Sum_By_Source.to_dict(orient='index')
Sum_By_Target = clean_flow.groupby('Target').agg({'Weight': 'sum'})
sum_by_target_dict = Sum_By_Target.to_dict(orient='index')


# %%
# create new dataframe columns to store total flow volume 
clean_flow['TotalOriginFlow'] = clean_flow.apply(lambda x: sum_by_source_dict[x['Source']]['Weight'], axis=1)
clean_flow['TotalDestinationFlow'] = clean_flow.apply(lambda x: sum_by_target_dict[x['Target']]['Weight'], axis=1)


# %%
clean_flow.head()


# %%
# create the pandas series for flows, Oi (total origin flows), Dj (total destination flows), Dij (flow between each pair of OD), Origin (origin nodes), Destination (destination nodes)
flows = clean_flow['Weight'].values
Oi = clean_flow['TotalOriginFlow'].values
Dj = clean_flow['TotalDestinationFlow'].values 
Dij = clean_flow['Weight'].values
Origin = clean_flow['Source'].values
Destination = clean_flow['Target'].values


# %%
import pysal


# %%
# improt four types of the spatial interaction model
from pysal.model.spint import Gravity
from pysal.model.spint import Attraction
from pysal.model.spint import Doubly
from pysal.model.spint import Production


# %%
help(Gravity) # get some information on how to use the model


# %%
# here we use a power function to estimate distnace-decay effect of spatial interaction
# other options available are an exponential function or other customised functions
# other parameters are kept as default
gravity = Gravity(flows, Oi, Dj, Dij, 'pow')


# %%
# print out model parameters: k-estimated beta coefficients
gravity.params


# %%
production = Production(flows, Origin, Dj, Dij, 'pow')


# %%
production.params


# %%
attraction = Attraction(flows, Destination, Oi, Dij, 'pow')


# %%
attraction.params


# %%
doubly = Doubly(flows, Origin, Destination, Dij, 'pow')
doubly.params[-1:]


# %%
R2, adjR2, SSI, SRMSE, AIC = [], [], [], [], []
model_name = ['grav', 'prod', 'att', 'doub']
col_names = ['R2', 'adjR2', 'AIC', 'SRMSE', 'SSI']
models = [gravity, production, attraction, doubly]


# %%
for model in models:
    R2.append(model.pseudoR2)
    adjR2.append(model.adj_pseudoR2)
    SSI.append(model.SSI)
    SRMSE.append(model.SRMSE)
    AIC.append(model.AIC)


# %%
cols = {'model_name': model_name,
'R2': R2,
'adjR2': adjR2,
'SSI': SSI,
'SRMSE': SRMSE,
'AIC': AIC }


# %%
data = pd.DataFrame(cols).set_index('model_name')
data[col_names]


# %%
pow_doubly = Doubly(flows, Origin, Destination, Dij, 'pow')
print('SRMSE for exp distance-decay: ', doubly.SRMSE)
pow_doubly = Doubly(flows, Origin, Destination, Dij, 'exp')
print('SRMSE for exp distance-decay: ', pow_doubly.SRMSE)

# %% [markdown]
# In generall we found that a global model with power function of distance decay is able to explain the observed OD flows to a very high degree (R2=93%). Among the 4 types of models, a doubly constrained model gives the highest R2 and adjusted R2, but is penalised for its complexity (high AIC value). Comparing the best performing doubly constrained model with a power function and an exponential function for distance decay, the result with power function gives a much higher R2 and Adj.R2.
# 
# This result by no means suggests that a global model is the best model to predict OD flows for several reasons:
# - Lack of consideration of local/spatial heterogeneity of flow patterns; requires a deeper exploration of why a global model gives such high R2 despite considerable local heterogeneity;
# - the OD flow data is only a subset of all mobility patterns; need a larger dataset to examine if the same finding can be generalised.

