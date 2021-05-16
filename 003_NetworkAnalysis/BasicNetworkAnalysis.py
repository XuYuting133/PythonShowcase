# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Basic Network Analysis with NetworkX
# In this demo we use networkx package to read/write a network, and generate fundamental network statistics e.g. degree ditribution, 

# %%
import networkx as nx 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt


# %%
# we can use in-built graph generator to create sample graphs based on different graph model
G = nx.complete_graph(50)   # this will create a completely connected graph with 50 nodes


# %%
# plot the graph
nx.draw(G)


# %%
# for demo purpose we plot a few other network types
fig, ax = plt.subplots(3, 4, figsize=(15,12))
G = nx.scale_free_graph(50)
nx.draw(nx.complete_graph(50), ax=ax[0,0])
nx.draw(nx.star_graph(50), ax=ax[0,1])
nx.draw(nx.circular_ladder_graph(50), ax=ax[0,2])
nx.draw(nx.ladder_graph(50), ax=ax[0,3])

nx.draw(nx.path_graph(50), ax=ax[1,0])
nx.draw(nx.wheel_graph(50), ax=ax[1,1])
nx.draw(nx.erdos_renyi_graph(50, 0.3), ax=ax[1,2])
nx.draw(nx.barabasi_albert_graph(50, 5), ax=ax[1,3])

nx.draw(nx.random_powerlaw_tree(10), ax=ax[2,0])
nx.draw(nx.scale_free_graph(50), ax=ax[2,1])
nx.draw(nx.karate_club_graph(), ax=ax[2,2])
nx.draw(nx.les_miserables_graph(), ax=ax[2,3])


# %% [markdown]
# ## Network Statistics 
# Calculate basic network statistics

# %%
# import an edgelist as a weighted directed graph
filepath = r"data/sample.edgelist"
G = nx.read_edgelist(filepath, create_using=nx.DiGraph,data=(('weight', int),), delimiter=' ')

# %% [markdown]
# This is a fairly large network

# %%
# here we calculate some network-level statistics to describe the network
# node / edge count
node_count = len(G.nodes)
edge_count = len(G.edges)
# calculate network density
graph_density = nx.density(G)
# average clustering coefficient
graph_avg_clustering_coef = nx.average_clustering(G)
# average neighbour degree
graph_avg_neighbour_deg = nx.average_neighbor_degree(G)
# k-nearest-neighbour
knn = nx.k_nearest_neighbors(G)
# average shortest path
graph_avg_shortest_path = nx.average_shortest_path_length(G)


# %%

print(f"The network has {node_count} nodes, {edge_count} edges, with average density of {graph_density}.\nAverage clustering coefficient = {graph_avg_clustering_coef}\nAverage shortest path length = {graph_avg_shortest_path}")

# %% [markdown]
# Many more network statistics are node-based or edge-based, i.e. the statistics describe individual node/edge in the network. For example, KNN, or average degree of nearest neighbours of k-degree nodes, is used to understand degree correlation and graph assortativity. By plotting KNN against k, we can understand if k-degree nodes tend to connect with nodes of similar degrees.

# %%
knn_df = pd.DataFrame.from_dict(knn,orient='index',columns=['KNN'])
knn_df.sort_index(inplace=True)
knn_df.head()


# %%
plt.figure(figsize=(15,15))
plt.scatter(knn_df.index, knn_df['KNN'], marker='x', alpha=0.7)
plt.xlim(0, 1000)
plt.ylim(0, 400)
plt.xlabel("Degree K")
plt.ylabel("Average Degree of Nearest Neighbours of Degree-K Node")
plt.plot([0, 1000], [0,1000], color='coral', linestyle=':') 
plt.gca().set_aspect('equal', adjustable='box')
plt.title("Knn(k)")

# %% [markdown]
# The result above suggests that the network is weakly disassortative with knn(k) below the degree of k. We calculate assortativity of the graph to verify.

# %%
print(nx.degree_assortativity_coefficient(G))

# %% [markdown]
# Indeed the degree assortativity coefficient is below 0 and suggests that the network is weakly disassortative.

# %%
# PageRank
pagerank_dict = nx.pagerank(G)
pagerank_df = pd.DataFrame.from_dict(pagerank_dict,orient='index',columns=['PR'])
pagerank_df.hist(bins=50,histtype='bar', density=True, color='blue', alpha=0.5)


# %%
# betweenness centrality
betweenness_dict = nx.betweenness_centrality(G)
betweenness_df = pd.DataFrame.from_dict(betweenness_dict, orient='index', columns=['Betweenness Centrality'])
betweenness_df.hist(bins=50, color='coral')


# %%
# node degrees
degrees = dict(G.degree())
degree_df = pd.DataFrame.from_dict(degrees, orient='index', columns=['Degrees'])
degree_df.hist(bins=50, color='green')


# %%
# weighted degrees
weighted_degrees = dict(G.degree(weight='weight'))
weighted_degree_df = pd.DataFrame.from_dict(weighted_degrees, orient='index', columns=['Weighted Degrees'])
weighted_degree_df.hist(bins=50, color='orange')


# %%
# concatenate all df
graph_df = pd.concat([degree_df, weighted_degree_df, pagerank_df, betweenness_df], axis=1)
graph_df.head()


# %%
fig, ax = plt.subplots(1, 2,figsize=(10,5))
ax[0].scatter(graph_df['Degrees'], graph_df['PR'], c='blue', alpha=0.05, s=3, label='PageRank')
ax[0].scatter(graph_df['Degrees'], graph_df['Betweenness Centrality'], c='r', alpha=0.3, s=1, label='Betweenness Centrality')
# ax[0].scatter(graph_df['Degrees'], graph_df['Weighted Degrees'], c='g', alpha=0.3, s=1)
ax[0].set_title("PR/Betweenness Centrality over Degrees") 

ax[1].scatter(graph_df['Betweenness Centrality'], graph_df['PR'], c='k', alpha=0.3, s=1, label='PageRank')
ax[1].set_title("PageRank over Betweenness Centrality")
plt.legend()
plt.show()

# %% [markdown]
# ## Community Detection
# Community Detection is frequently used in spatial networks to identify spatial clusters in the network that could correspond to e.g. administrative regions. There are many algorithms to identify communities. Some of the common ones include Girvan-Newman, Louvain's Modularity, Label Propagation and so on. With a large-size network the process may take long. Here we generate a random small-size network for demonstration.

# %%
# apply Girvan-Newman algorithm
sample_g = nx.karate_club_graph()
gm_communities = nx.algorithms.community.girvan_newman(sample_g)
top_comm = next(gm_communities)
sorted(map(sorted, top_comm))


# %%
# apply greedy algorithm to detect community
greedy_comms = nx.algorithms.community.greedy_modularity_communities(sample_g)
greedy_comms


# %%
# one common algorithm used in spatial network is Louvains' Modularity. It can be generated by another package Community
import community as community_louvain
# convert DiGraph to undirected
undirected_G = G.to_undirected()
louvain_comms = community_louvain.best_partition(undirected_G, weight='weight')


# %%
louvain_df = pd.DataFrame([(k, v) for k, v in louvain_comms.items()], columns=['NodeID', 'LouvainCommunity'])
louvain_df.head()


# %%
louvain_df.info()


# %%
# we now append Louvain Community info to the transit nodes (transit nodes) and illustrate communities spatially
import geopandas
transit_nodes_gdf = geopandas.read_file(r"data/TransitNodes.shp")
transit_nodes_gdf.head()


# %%
transit_nodes_gdf.info()


# %%
# join the two dataFrame
transit_nodes_w_comm_gdf = pd.merge(left=transit_nodes_gdf, right=louvain_df, left_on="BUS_STOP_N", right_on='NodeID')
all_graph_gdf = pd.merge(left=transit_nodes_w_comm_gdf, right=graph_df, left_on="BUS_STOP_N", right_index=True)
all_graph_gdf.head()

# %% [markdown]
# We now have a dataframe of all node-based statistics that we have calculated so far. We will map it out with geopandas.

# %%
import matplotlib.colors as colors
fig, ax = plt.subplots(2, 3, figsize=(20, 10))
all_graph_gdf.plot(markersize=1, ax=ax[0][0], color='k')
ax[0][0].title.set_text("Transit Nodes Location")
all_graph_gdf.plot(column='LouvainCommunity', markersize=1, cmap="tab20", ax=ax[0][1])
ax[0][1].title.set_text("Community")
all_graph_gdf.plot(column="PR", cmap="Reds", ax=ax[0][2], markersize=1, norm=colors.PowerNorm(gamma=0.5))
ax[0][2].title.set_text("PageRank")
all_graph_gdf.plot(column="Degrees", cmap="Reds", ax=ax[1][0], markersize=1, norm=colors.PowerNorm(gamma=0.5))
ax[1][0].title.set_text("Degrees")
all_graph_gdf.plot(column="Weighted Degrees", cmap="Reds",  ax=ax[1][1], markersize=1, norm=colors.PowerNorm(gamma=0.5))
ax[1][1].title.set_text("Weighted Degrees")
all_graph_gdf.plot(column="Betweenness Centrality", cmap="Reds", ax=ax[1][2], markersize=1, norm=colors.PowerNorm(gamma=0.5))
ax[1][2].title.set_text("Betweenness Centrality")

# %% [markdown]
# Results from Louvain's Community Detection algorithm suggest that space has a strong effect in the formation of communities in this case, since most nodes that belong to the same community also tend to be spatially closed to one another, forming somewhat spatially contiguous regions.

# %%



