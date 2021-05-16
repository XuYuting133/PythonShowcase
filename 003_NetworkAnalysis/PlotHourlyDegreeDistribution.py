# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
import numpy as np
import seaborn as sns
import os, sys
import matplotlib.pyplot as plt


# %%
folder = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\Processed\202101\Node\Bus"
file_list = os.listdir(folder)
note_attr_files = [f for f in file_list if "NodeAttributes_" in f and ".csv" in f]
len(note_attr_files)


# %%
from collections import defaultdict
node_attr_data_list = {}
for f in note_attr_files:
    # print(f)
    df = pd.read_csv(os.path.join(folder, f)) 
    
    
    degree_sum = len(df['Degree'])
    degree_count = df['Degree'].value_counts().to_dict()
    df['Degree_Count'] = df['Degree'].apply(lambda x:degree_count[x])
    df['Degree_Freq'] = df['Degree_Count']/degree_sum
    df['LogDegreeCount'] = np.log10(df["Degree_Count"].replace(0, np.nan))
    df['LogDegreeFreq'] = np.log10(df["Degree_Freq"].replace(0, np.nan))
    df['LogDegree'] = np.log10(df["Degree"].replace(0, np.nan))
    
    in_degree_sum = len(df['indegree'])
    in_degree_count = df['indegree'].value_counts().to_dict()
    df['in_degree_count'] = df['indegree'].apply(lambda x:in_degree_count[x])
    df['in_degree_freq'] = df['in_degree_count']/in_degree_sum
    df['LogInDegreeCount'] = np.log10(df["in_degree_count"].replace(0, np.nan))
    df['LogInDegreeFreq'] = np.log10(df["in_degree_freq"].replace(0, np.nan))
    df['LogInDegree'] = np.log10(df["indegree"].replace(0, np.nan))
    
    out_degree_sum = len(df['outdegree'])
    out_degree_count = df['outdegree'].value_counts().to_dict()
    df['out_degree_count'] = df['outdegree'].apply(lambda x:out_degree_count[x])
    df['out_degree_freq'] = df['out_degree_count']/out_degree_sum
    df['LogOutDegreeCount'] = np.log10(df["out_degree_count"].replace(0, np.nan))
    df['LogOutDegreeFreq'] = np.log10(df["out_degree_freq"].replace(0, np.nan))
    df['LogOutDegree'] = np.log10(df["outdegree"].replace(0, np.nan))
    
    
    df['DayType'] = f.split("_")[2]
    df['DayHourInt'] = int(f.replace(".csv","").split("_")[-1])
    df['DayHourTxt'] = f.replace(".csv","").split("_")[-1]
    df_name = f.replace(".csv","")[15:]
    node_attr_data_list[df_name] = df
    #print(df.columns)


# %%
df.columns


# %%
# merge df into one
degree_df = pd.DataFrame()
for df_name in node_attr_data_list.keys():
    degree_df=degree_df.append(node_attr_data_list[df_name],ignore_index=True)
    
weekday_df = degree_df[degree_df['DayType']=='WEEKDAY']
weekend_df = degree_df[degree_df['DayType']=='WEEKEND']

# remove null value from LogDegree

weekend_df = weekend_df[weekend_df['LogDegree'].notna()]
weekday_df = weekday_df[weekday_df['LogDegree'].notna()]


# %%
degree_df.shape


# %%
import scipy.stats as stats


# %%
all_df = weekday_df.append(weekend_df)
all_df.columns


# %%
fig, axes = plt.subplots(4,6, figsize=(16,12), constrained_layout=True)
fig.suptitle('Degree Frequency Distribution By Hour', )

count = 0
color_dict = dict({'WEEKEND':'black',
                  'WEEKDAY':'red'})

while count < 24:
    
    x = count%6
    y = int(count/6)
    
    for day_type in ['WEEKDAY','WEEKEND']:
    
        sub_df = all_df[all_df['DayHourInt']==count]
        if count==5:
            legend=True
        else:
            legend=False
        
        # indegree
        sns.scatterplot(ax=axes[y][x],
                        x=sub_df[sub_df['DayType']==day_type]["indegree"], 
                        y=sub_df[sub_df['DayType']==day_type]["in_degree_freq"],
                        alpha=0.01, s=10,
                       hue=sub_df[sub_df['DayType']==day_type]["DayType"],palette=color_dict, marker='+',legend=False)
        # outdegree
        sns.scatterplot(ax=axes[y][x],
                        x=sub_df[sub_df['DayType']==day_type]["outdegree"], 
                        y=sub_df[sub_df['DayType']==day_type]["out_degree_freq"],
                        alpha=0.01, s=10,
                       hue=sub_df[sub_df['DayType']==day_type]["DayType"],palette=color_dict, legend=False)
        
        
    axes[y][x].set_title("Hour Of Day: " + str(count),fontweight="bold", size=12)
    axes[y][x].set_xlim([0, 500])
    axes[y][x].set_ylim([0, 0.1])
    count+=1   
#plt.legend(bbox_to_anchor=(1.01, 1.01))


# %%
# Log Degree Frequency
fig, axes = plt.subplots(4,6, figsize=(16,10), sharex=True, sharey=True, constrained_layout=True)
fig.suptitle('Logarithmic Degree Distribution By Hour', fontsize=20)

count = 0
color_dict = dict({'WEEKEND':'black',
                  'WEEKDAY':'red'})

while count < 24:
    
    x = count%6
    y = int(count/6)
    sub_df = all_df[all_df['DayHourInt']==count]
        
    # weekend indegree
    sns.regplot(x=sub_df[sub_df['DayType']=='WEEKEND']['LogInDegree'],
                y=sub_df[sub_df['DayType']=='WEEKEND']['LogInDegreeFreq'], ax=axes[y][x],
            scatter_kws={'alpha':0.01,'s':1},line_kws={"lw":1,"ls":"--"}, color='black',label=False)
        
    # weekend outdegree
    sns.regplot(x=sub_df[sub_df['DayType']=='WEEKEND']['LogOutDegree'],
                y=sub_df[sub_df['DayType']=='WEEKEND']['LogOutDegreeFreq'], ax=axes[y][x],
            scatter_kws={'alpha':0.01,'s':1},line_kws={"lw":1,"ls":":"}, color='gray',label=False)

    # weekday indegree
    sns.regplot(x=sub_df[sub_df['DayType']=='WEEKDAY']['LogInDegree'],
                y=sub_df[sub_df['DayType']=='WEEKDAY']['LogInDegreeFreq'], ax=axes[y][x],
            scatter_kws={'alpha':0.01,'s':1},line_kws={"lw":1,"ls":"--"}, color='red',label=False)
        
    # weekday outdegree
    sns.regplot(x=sub_df[sub_df['DayType']=='WEEKDAY']['LogOutDegree'],
                y=sub_df[sub_df['DayType']=='WEEKDAY']['LogOutDegreeFreq'], ax=axes[y][x],
            scatter_kws={'alpha':0.01,'s':1},line_kws={"lw":1,"ls":":"}, color='pink',label=False)
    
    
        
    axes[y][x].set_title("Hour Of Day: " + str(count), size=12)
    
    if y==3:
        axes[y][x].set_xlabel("log(k)")
    else:
        axes[y][x].set_xlabel("")
    if x==0:
        axes[y][x].set_ylabel("log(Pk)")
    else:
        axes[y][x].set_ylabel("")
    count+=1   
#plt.legend(bbox_to_anchor=(1.01, 1.01))


# %%
fig, axes = plt.subplots(1, 2, sharex=True, figsize=(16,5))
fig.suptitle('Degree Count By Hour')

sns.scatterplot(ax=axes[0],x=weekday_df["Degree"], y=weekday_df["Degree_Count"],
                alpha=0.01, s=5,hue=weekday_df['DayHourTxt'],legend=False, palette='tab10')
axes[0].set_title("Weekday")

sns.scatterplot(ax=axes[1],x=weekend_df["Degree"], y=weekend_df["Degree_Count"],
                alpha=0.01, s=5, hue=weekend_df['DayHourTxt'], palette = 'tab10')
axes[1].set_title("Weekend")

plt.legend(bbox_to_anchor=(1.01, -0.2),ncol=12)
#plt.legend(bbox_to_anchor=(1.01, 1.01),borderaxespad=0)
#plt.tight_layout()


# %%
# overall knn plot

# distribution of Degree vs KNN
fig, axes = plt.subplots(4,6, figsize=(16,10), sharex=True, sharey=True, constrained_layout=True)
fig.suptitle('knn(k) vs k',fontweight="bold", size=20)

count = 0
for key in weekday_knn.keys():

    x = count%6
    y = int(count/6)
    dn = pd.DataFrame(list(weekday_knn[key].items()),columns = ['Degree','AvgDegreeKNN']) 
    dn_weekend = pd.DataFrame(list(weekend_knn[key].items()),columns = ['Degree','AvgDegreeKNN']) 
    
    dn['LogDegree'] = np.log10(dn["Degree"].replace(0, np.nan))
    dn['LogAvgDegreeKNN'] = np.log10(dn["AvgDegreeKNN"].replace(0, np.nan))
     
    dn_weekend['LogDegree'] = np.log10(dn_weekend["Degree"].replace(0, np.nan))
    dn_weekend['LogAvgDegreeKNN'] = np.log10(dn_weekend["AvgDegreeKNN"].replace(0, np.nan))

    # sns.scatterplot(data=dn, x="Degree",y="AvgDegreeKNN",ax=axes[y][x], alpha=0.05)
    axes[y][x].scatter(x=dn["Degree"], y=dn["AvgDegreeKNN"], alpha=0.1, color='r', s=5)
    axes[y][x].scatter(x=dn_weekend["Degree"], y=dn_weekend["AvgDegreeKNN"], alpha=0.1, color='k', s=5)
    axes[y][x].plot([0, 1], [0, 1], color='gray', transform=axes[y][x].transAxes, linestyle='--')  
    
    #grid = sns.lmplot(data=dn, x="Degree", y="AvgDegreeKNN", ax=axes[y][x])
    #grid.plot_joint(plt.scatter, color="g")
    #plt.plot([0, 4], [1.5, 0], linewidth=2)
    
    axes[y][x].set_title("Hour Of Day: " + str(key), size=12)
    axes[y][x].set_ylabel("knn(k)")
    axes[y][x].set_xlabel("k")

    count += 1    
    
plt.show()


# %%
new_df = weekend_df.append(weekday_df)


# %%
new_df.columns


# %%
fig = plt.figure(num=None, figsize=(10, 8), dpi=80, facecolor='w', edgecolor='k')
plt.rcParams['axes.facecolor'] = 'w'
ax1 = fig.add_subplot(111)

plt.title('Degree Distribution', fontweight=40)
#sns.scatterplot(x=new_df["Degree"], y=new_df["Degree_Freq"],alpha=0.01, 
#                hue=new_df['DayType'],size=0.001, style=new_df['DayType'],palette={'WEEKEND':'red',"WEEKDAY":'black'})

ax1.scatter(weekend_df['indegree'],weekend_df['in_degree_freq'], s=10, c='k', marker="o", 
            label='Weekend In-Degree', alpha=1)
ax1.scatter(weekend_df['outdegree'],weekend_df['out_degree_freq'], s=10, c='lightgray', marker="o", 
            label='Weekend Out-Degree', alpha=1)
ax1.scatter(weekday_df['indegree'],weekday_df['in_degree_freq'], s=10, c='red', marker="o", 
            label='Weekday In-Degree', alpha=1)
ax1.scatter(weekday_df['outdegree'],weekday_df['out_degree_freq'], s=10, c='pink', marker="o", 
            label='Weekday In-Degree', alpha=1)

ax1.set_xlabel("k")
ax1.set_ylabel("Pk")
ax1.legend()
plt.show()


# %%
fig2 = plt.figure(num=None, figsize=(10, 8), dpi=80, facecolor='w', edgecolor='k')
ax2 = fig2.add_subplot(111)

plt.title('Log-Log Degree Distribution', fontweight=40)

# plot scatter plot
#ax2.scatter(weekend_df['LogInDegree'],weekend_df['LogInDegreeFreq'], s=10, c='k', marker="o", 
#           label='Weekend In-Degree', alpha=0.01)
#ax2.scatter(weekend_df['LogOutDegree'],weekend_df['LogOutDegreeFreq'], s=10, c='lightgray', marker="o", 
#            label='Weekend Out-Degree', alpha=0.01)
#ax2.scatter(weekday_df['LogInDegree'],weekday_df['LogInDegreeFreq'], s=10, c='red', marker="o", 
#            label='Weekday In-Degree', alpha=0.01)
#ax2.scatter(weekday_df['LogOutDegree'],weekday_df['LogOutDegreeFreq'], s=10, c='pink', marker="o", 
#            label='Weekday In-Degree', alpha=0.01)
sns.regplot(x=weekend_df['LogInDegree'],y=weekend_df['LogInDegreeFreq'], ax=ax2,color='k',
            scatter_kws={'alpha':0.01,'s':10},line_kws={"lw":1,"ls":"--"},label='Weekend In-Degree')
sns.regplot(x=weekend_df['LogOutDegree'],y=weekend_df['LogOutDegreeFreq'], ax=ax2, color='gray',
            scatter_kws={'alpha':0.01,'s':10},line_kws={"lw":1,"ls":"--"}, label='Weekend Out-Degree')

sns.regplot(x=weekday_df['LogInDegree'],y=weekday_df['LogInDegreeFreq'], ax=ax2,color='r', marker='+',
            scatter_kws={'alpha':0.01,'s':10},line_kws={"lw":1,"ls":"--"}, label='Weekday In-Degree')
sns.regplot(x=weekday_df['LogOutDegree'],y=weekday_df['LogOutDegreeFreq'], ax=ax2, color='pink', marker='+',
            scatter_kws={'alpha':0.01,'s':10},line_kws={"lw":1,"ls":"--"}, label='Weekday Out-Degree')

ax2.set_xlabel("log(k)")
ax2.set_ylabel("log(Pk)")
ax2.legend()
plt.show()


# %%
# get the regression formula
from scipy import stats

count = 0
while count < 24:
    
    x = count%6
    y = int(count/6)
    
    sub_df = all_df[(all_df['DayHourInt']==count) & (all_df['DayType']=='WEEKDAY')]
    mask = ~np.isnan(sub_df['LogInDegree']) & ~np.isnan(sub_df['LogInDegreeFreq'])
    slope, intercept, r_value, p_value, std_err = stats.linregress(sub_df['LogInDegree'][mask], 
                                                               sub_df['LogInDegreeFreq'][mask])
    
    # use line_kws to set line label for legend
    print("{0}|Weekday in-degree|{1:.5f}|{2:.5f}".format(count, slope, intercept))
    
    mask = ~np.isnan(sub_df['LogOutDegree']) & ~np.isnan(sub_df['LogOutDegreeFreq'])
    slope, intercept, r_value, p_value, std_err = stats.linregress(sub_df['LogOutDegree'][mask], 
                                                               sub_df['LogOutDegreeFreq'][mask])
    
    # use line_kws to set line label for legend
    print("{0}|Weekday out-degree|{1:.5f}|{2:.5f}".format(count,slope,intercept))
    
    sub_df = all_df[(all_df['DayHourInt']==count) & (all_df['DayType']=='WEEKEND')]
    mask = ~np.isnan(sub_df['LogInDegree']) & ~np.isnan(sub_df['LogInDegreeFreq'])
    slope, intercept, r_value, p_value, std_err = stats.linregress(sub_df['LogInDegree'][mask], 
                                                               sub_df['LogInDegreeFreq'][mask])
    # use line_kws to set line label for legend
    print("{0}|Weekend in-degree|{1:.5f}|{2:.5f}".format(count,slope,intercept))
    
    mask = ~np.isnan(sub_df['LogOutDegree']) & ~np.isnan(sub_df['LogOutDegreeFreq'])
    slope, intercept, r_value, p_value, std_err = stats.linregress(sub_df['LogOutDegree'][mask], 
                                                               sub_df['LogOutDegreeFreq'][mask])
    # use line_kws to set line label for legend
    print("{0}|Weekend out-degree|{1:.5f}|{2:.5f}".format(count,slope,intercept))
    
    count += 1


# %%
## Backup
# plot Weekend in-degree fit line
z1 = np.polyfit(weekend_df["LogInDegree"], weekend_df["LogInDegreeFreq"], 1)
p1 = np.poly1d(z1)(weekend_df["LogInDegree"])
ax2.plot(weekend_df["LogInDegree"],p1,"k:", lw=2, alpha=0.5)

# plot weekday fit line
z2 = np.polyfit(weekday_df["LogOutDegree"], weekday_df["LogOutDegreeFreq"], 1)
p2 = np.poly1d(z2)(weekday_df["LogOutDegree"])
ax2.plot(weekday_df["LogOutDegree"],p2,"r:", lw=2, alpha=0.5)

# plot Weekend fit line
z3 = np.polyfit(weekend_df["LogInDegree"], weekend_df["LogInDegreeFreq"], 1)
p3 = np.poly1d(z3)(weekend_Df["LogInDegree"])
ax2.plot(weekend_df["LogInDegree"],p3,"k--", lw=2, alpha=0.5)

# plot weekday fit line
z4 = np.polyfit(weekday_df["LogOutDegree"], weekday_df["LogOutDegreeFreq"], 1)
p4 = np.poly1d(z4)(weekday_df["LogOutDegree"])
ax2.plot(nweekday_df["LogOutDegree"],p4,"r:", lw=2, alpha=0.5)


# %%
new_df = weekday_df.append(weekend_df)
new_df.head()


# %%
# take log Day Degree Count
new_df['LogDayDegreeCount'] = np.log10(new_df["DayDegreeCount"].replace(0, np.nan))
new_df.head()


# %%
plt.title('Degree Distribution')
sns.scatterplot(x=new_df["LogDegree"], y=new_df["LogDayDegreeCount"],alpha=0.01, hue=new_df['DayHourInt'])
plt.show()


# %%
day_cmap = sns.diverging_palette(250, 30, l=65, center="dark", as_cmap=True)


# %%
sns.displot(degree_df, x="clustering", hue='DayHourIt', kind='kde',palette=day_cmap,alpha=0.5,linewidth=2)


# %%


# %% [markdown]
# # Create Graphs for Every Hour and Day Type

# %%
import networkx as nx
import os
from collections import defaultdict


# %%
input_data_folder = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\Processed\202101\Edge\Bus"
file_list = os.listdir(input_data_folder)
edgelist_list = [f for f in file_list if ".edgelist" in f]

graph_dict = defaultdict(nx.DiGraph)

for edgelist_filename in edgelist_list:
    #print(edgelist_filename)

    year_month = edgelist_filename.split("_")[1]
    day_type = edgelist_filename.split("_")[2]
    hour = edgelist_filename.split("_")[-1].split(".")[0]  # in text

    graph_name = "{}_{}_{}".format(year_month, day_type, hour)

    edge_list = os.path.join(input_data_folder, edgelist_filename)
    if not os.path.exists(edge_list):
        continue

    new_graph = nx.read_weighted_edgelist(edge_list)
    graph_dict[graph_name] = new_graph


# %%
knn_dict = {}
degree_dict = {}

for graph in graph_dict.keys():
    print(graph)
    knn_dict[graph] = nx.k_nearest_neighbors(graph_dict[graph], weight='weight')
    degree_dict[graph] = {(x):y for (x,y) in graph_dict[graph].degree(weight='weight')}

    


# %%
# split dict to weekend vs weekday
weekday_knn = {}
weekend_knn = {}

for key in knn_dict.keys():
    
    day_type = key.split("_")[1]
    day_hour = int(key.split("_")[-1])
    
    if day_type=="WEEKDAY":
        weekday_knn[day_hour] = knn_dict[key]
    else:
        weekend_knn[day_hour] = knn_dict[key]
        
weekday_knn = dict(sorted(weekday_knn.items()))
weekend_knn = dict(sorted(weekend_knn.items()))


# %%
# distribution of Degree vs KNN
fig, axes = plt.subplots(4,6, figsize=(16,12), constrained_layout=True)
fig.suptitle('Average Degree of k-nearest neighbours vs Degree (Weekday)',fontweight="bold", size=20)

count = 0
for key in weekday_knn.keys():

    x = count%6
    y = int(count/6)
    dn = pd.DataFrame(list(weekday_knn[key].items()),columns = ['Degree','AvgDegreeKNN']) 
    dn['LogDegree'] = np.log10(dn["Degree"].replace(0, np.nan))
    dn['LogAvgDegreeKNN'] = np.log10(dn["AvgDegreeKNN"].replace(0, np.nan))

    # sns.scatterplot(data=dn, x="Degree",y="AvgDegreeKNN",ax=axes[y][x], alpha=0.05)
    axes[y][x].scatter(x=dn["Degree"], y=dn["AvgDegreeKNN"], alpha=0.1)
    axes[y][x].plot([0, 1], [0, 1], color='red', transform=axes[y][x].transAxes)  
    
    #grid = sns.lmplot(data=dn, x="Degree", y="AvgDegreeKNN", ax=axes[y][x])
    #grid.plot_joint(plt.scatter, color="g")
    #plt.plot([0, 4], [1.5, 0], linewidth=2)
    
    axes[y][x].set_title("Hour Of Day: " + str(key),fontweight="bold", size=12)
    axes[y][x].set_xlim([0, 600])
    axes[y][x].set_ylim([0, 600])

    count += 1    
    
plt.show()


# %%



# %%
# distribution of Degree vs KNN
fig, axes = plt.subplots(4,6, figsize=(16,12), sharex=True, sharey=True, constrained_layout=True)
fig.suptitle('Log Average Degree of k-nearest neighbours vs Log Degree (Weekday)',fontweight="bold", size=20)

count = 0
for key in weekday_knn.keys():

    x = count%6
    y = int(count/6)
    dn = pd.DataFrame(list(weekday_knn[key].items()),columns = ['Degree','AvgDegreeKNN']) 
    dn['LogDegree'] = np.log10(dn["Degree"].replace(0, np.nan))
    dn['LogAvgDegreeKNN'] = np.log10(dn["AvgDegreeKNN"].replace(0, np.nan))

    # sns.scatterplot(data=dn, x="Degree",y="AvgDegreeKNN",ax=axes[y][x], alpha=0.05)
    axes[y][x].scatter(x=dn["LogDegree"], y=dn["LogAvgDegreeKNN"], alpha=0.1)
    axes[y][x].axhline(y=np.mean(dn['LogAvgDegreeKNN']),xmin=0,xmax=3,c="gray",linewidth=1,zorder=0)
    
    z = np.polyfit(dn["LogDegree"], dn["LogAvgDegreeKNN"], 1)
    p = np.poly1d(z)(dn["LogDegree"])
    axes[y][x].plot(dn["LogDegree"],p,"r--", lw=1, alpha=0.5)
 
    
    #grid = sns.lmplot(data=dn, x="Degree", y="AvgDegreeKNN", ax=axes[y][x])
    #grid.plot_joint(plt.scatter, color="g")
    #plt.plot([0, 4], [1.5, 0], linewidth=2)
    
    axes[y][x].set_title("Hour Of Day: " + str(key),fontweight="bold", size=12)
    #axes[y][x].set_xlim([0, 3])
    #axes[y][x].set_ylim([0, 3])

    count += 1    
    
plt.show()


# %%
# distribution of Degree vs KNN
fig, axes = plt.subplots(4,6, figsize=(16,12), constrained_layout=True)
fig.suptitle('Average Degree of k-nearest neighbours vs Degree (Weekend)',fontweight="bold", size=20)

count = 0
for key in weekend_knn.keys():

    x = count%6
    y = int(count/6)
    dn = pd.DataFrame(list(weekend_knn[key].items()),columns = ['Degree','AvgDegreeKNN']) 

    # sns.scatterplot(data=dn, x="Degree",y="AvgDegreeKNN",ax=axes[y][x], alpha=0.05)
    axes[y][x].scatter(x=dn["Degree"], y=dn["AvgDegreeKNN"], alpha=0.1)
    axes[y][x].plot([0, 1], [0, 1], color='red', transform=axes[y][x].transAxes)  
    
    #grid = sns.lmplot(data=dn, x="Degree", y="AvgDegreeKNN", ax=axes[y][x])
    #grid.plot_joint(plt.scatter, color="g")
    #plt.plot([0, 4], [1.5, 0], linewidth=2)
    
    axes[y][x].set_title("Hour Of Day: " + str(key),fontweight="bold", size=12)
    axes[y][x].set_xlim([0, 600])
    axes[y][x].set_ylim([0, 600])

    count += 1    
    
plt.show()


# %%
# distribution of Degree vs KNN
fig, axes = plt.subplots(4,6, figsize=(16,12), sharex=True, sharey=True, constrained_layout=True)
fig.suptitle('Log Average Degree of k-nearest neighbours vs Log Degree (Weekend)',fontweight="bold", size=20)

count = 0
for key in weekend_knn.keys():

    x = count%6
    y = int(count/6)
    dn = pd.DataFrame(list(weekend_knn[key].items()),columns = ['Degree','AvgDegreeKNN']) 
    dn['LogDegree'] = np.log10(dn["Degree"].replace(0, np.nan))
    dn['LogAvgDegreeKNN'] = np.log10(dn["AvgDegreeKNN"].replace(0, np.nan))

    # sns.scatterplot(data=dn, x="Degree",y="AvgDegreeKNN",ax=axes[y][x], alpha=0.05)
    axes[y][x].scatter(x=dn["LogDegree"], y=dn["LogAvgDegreeKNN"], alpha=0.1)
    axes[y][x].axhline(y=np.mean(dn['LogAvgDegreeKNN']),xmin=0,xmax=3,c="gray",linewidth=1,zorder=0)
    
    z = np.polyfit(dn["LogDegree"], dn["LogAvgDegreeKNN"], 1)
    p = np.poly1d(z)(dn["LogDegree"])
    axes[y][x].plot(dn["LogDegree"],p,"r--", lw=1, alpha=0.5)
 
    
    #grid = sns.lmplot(data=dn, x="Degree", y="AvgDegreeKNN", ax=axes[y][x])
    #grid.plot_joint(plt.scatter, color="g")
    #plt.plot([0, 4], [1.5, 0], linewidth=2)
    
    axes[y][x].set_title("Hour Of Day: " + str(key),fontweight="bold", size=12)
    #axes[y][x].set_xlim([0, 3])
    #axes[y][x].set_ylim([0, 3])

    count += 1    
    
plt.show()


# %%



# %%
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# %% [markdown]
# # Plot Joint Degree Distribution through Graphs

# %%
graph_dict.keys()


# %%
weekday_graph = dict(sorted({int(graph.split("_")[-1]):graph_dict[graph] for graph in graph_dict.keys() if "WEEKDAY" in graph}.items()))
weekend_graph = dict(sorted({int(graph.split("_")[-1]):graph_dict[graph] for graph in graph_dict.keys() if "WEEKEND" in graph}.items()))


# %%
weekday_graph.keys()


# %%
# get joint distribution df: SourceDegree, DestDegree
weekday_joint_degree_dist_df = {}
for day_hour in weekday_graph.keys():
    
    G = weekday_graph[day_hour]
    
    source_dest_degree = {'SourceDegree':[], 'DestDegree':[]}
    
    edge_list = G.edges()
    for edge in edge_list:
        source_node = edge[0]
        dest_node = edge[1]
        
        source_dest_degree['SourceDegree'].append(G.degree[source_node])
        source_dest_degree['DestDegree'].append(G.degree[dest_node])
       
        
    weekday_joint_degree_dist_df[day_hour] = pd.DataFrame(source_dest_degree)

len(weekday_joint_degree_dist_df)


# %%
# get joint distribution df: SourceDegree, DestDegree
weekend_joint_degree_dist_df = {}
for day_hour in weekend_graph.keys():
    
    G = weekend_graph[day_hour]
    
    source_dest_degree = {'SourceDegree':[], 'DestDegree':[]}
    
    edge_list = G.edges()
    for edge in edge_list:
        source_node = edge[0]
        dest_node = edge[1]
        
        source_dest_degree['SourceDegree'].append(G.degree[source_node])
        source_dest_degree['DestDegree'].append(G.degree[dest_node])
        
        
    weekend_joint_degree_dist_df[day_hour] = pd.DataFrame(source_dest_degree)

len(weekend_joint_degree_dist_df)


# %%
fig, axes = plt.subplots(4,6, figsize=(16,10), sharex=True, sharey=True, constrained_layout=True)
fig.suptitle('Joint Degree Distribution (Weekday) - scatter plot',fontweight="bold", size=20)
    
for day_hour in weekday_joint_degree_dist_df.keys():
    
    x = day_hour%6
    y = int(day_hour/6)
    
    hour_df = weekday_joint_degree_dist_df[day_hour]
    hour_df['LogSourceDegree'] = np.log(hour_df['SourceDegree'].replace(0, np.nan))
    hour_df['LogDestDegree'] = np.log(hour_df['DestDegree'].replace(0, np.nan))
    
    axes[y][x].scatter(x=hour_df['LogSourceDegree'], y=hour_df['LogDestDegree'], alpha=0.01, c='maroon')
    axes[y][x].set_title("Hour Of Day: " + str(day_hour), fontweight="bold", size=12)
    


# %%
from scipy.stats import kde

fig, axes = plt.subplots(4,6, figsize=(16,10), sharex=True, sharey=True, constrained_layout=True)
fig.suptitle('Joint Degree Distribution (Weekday) - KDE Density',fontweight="bold", size=20)

for day_hour in weekday_joint_degree_dist_df.keys():
    
    i = day_hour%6
    j = int(day_hour/6)
    
    hour_df = weekday_joint_degree_dist_df[day_hour]
    hour_df['LogSourceDegree'] = np.log(hour_df['SourceDegree'].replace(0, np.nan))
    hour_df['LogDestDegree'] = np.log(hour_df['DestDegree'].replace(0, np.nan))
    
    x = hour_df['LogSourceDegree']
    y = hour_df['LogDestDegree']
    
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)(x)
    axes[j][i].plot(x, p,"r--", lw=1, alpha=0.5)
    
    axes[j][i].set_title("{}:00".format(str(day_hour).zfill(2)), fontweight=10)
    
      
    sns.kdeplot(x=x, y=y, cmap="Reds", shade=True, bw_adjust=.5, ax=axes[j][i])
    
plt.show()


# %%
fig, axes = plt.subplots(4,6, figsize=(16,10), sharex=True, sharey=True, constrained_layout=True)
fig.suptitle('Joint Degree Distribution (Weekend) - KDE Density',fontweight="bold", size=20)

for day_hour in weekend_joint_degree_dist_df.keys():
    
    i = day_hour%6
    j = int(day_hour/6)
    
    hour_df = weekend_joint_degree_dist_df[day_hour]
    hour_df['LogSourceDegree'] = np.log(hour_df['SourceDegree'].replace(0, np.nan))
    hour_df['LogDestDegree'] = np.log(hour_df['DestDegree'].replace(0, np.nan))
    
    x = hour_df['LogSourceDegree']
    y = hour_df['LogDestDegree']
    
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)(x)
    axes[j][i].plot(x, p,"r--", lw=1, alpha=0.5)
    
    axes[j][i].set_title("{}:00".format(str(day_hour).zfill(2)), fontweight=10)
    
      
    sns.kdeplot(x=x, y=y, cmap="Reds", shade=True, bw_adjust=.5, ax=axes[j][i])
    
plt.show()


