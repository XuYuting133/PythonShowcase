# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Predicting Scooter Users
# April 2020
# 
# Part 2. Exploratory Data Analysis
# 
# Submitted by: XU Yuting
# %% [markdown]
# ## Section 1. Import Data

# %%
# import relevant libraries
import sys
import pandas as pd
import pyodbc
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# %%
# connect to SQL server database
# for confidentiality purpose I have removed database connection details
conn = pyodbc.connect()
sql_query = "select date, hr, weather, temperature, feels_like_temperature, relative_humidity, windspeed, psi, guest_scooter from rental_data where date between '2011-01-01' and '2012-12-31'"

# load the datset into Pandas dataframe, df
df = pd.io.sql.read_sql(sql_query,conn)

# %% [markdown]
# ## Section 2. Examine the data columns

# %%
df.info()


# %%
df.describe()

# %% [markdown]
# Bearing in mind that the purpose of the exercise is to predict the number of scooters, given the other variables, we have to pay attention to the 'guest_scooter' column, and understand that this is a numeric continous attribute.

# %%
df.head()

# %% [markdown]
# From the above we can see that:
# - There are negative values in the column "guest_scooter" --> the negative values can't be true, so they will need to be removed
# - Column 'weather' contains non-numeric values --> this will need to be scrutinized in detail and transformed to numeric values
# - Column 'date' is not numeric either --> we can extract the numeric attributes out into year, month, date
# - Column 'relative_humidity' and 'psi' contains value 0 --> This is quite unrealistic, so we can treat them as missing value too
# %% [markdown]
# We will take a closer look at the 'weather' column

# %%
df['weather'].value_counts()

# %% [markdown]
# Looks like 'weather' column is not so clean: there are typo errors and misspellings that will need to be cleaned up before they can be transformed to numeric values.
# %% [markdown]
# By examining the data columns above, we have concluded that there are some data cleaning/preprocessing tasks we will need to perform:
# - Column 'weather': clean up the typos, and transform to numeric data
# - Column 'guest_scooter': remove negative values
# - Column 'relative_humidity','psi': value 0 should be treated as null values
# - Column 'date': transform to numeric data e.g. year, month, date, day of week
# 
# With these tasks in mind, we can now start to preprocess the data
# %% [markdown]
# ## Section 3. Data Cleaning & Preprocessing
# %% [markdown]
# #### Task 1: Column 'Weather' -- Clean up typos and transform categorical data to numeric data

# %%
df['weather']=df['weather'].str.upper()
df['weather'].value_counts()


# %%
# now we correct some of the spellings
df.loc[df['weather']=='LEAR','weather']='CLEAR'
df.loc[df['weather']=='CLAR','weather']='CLEAR'
df.loc[df['weather']=='CLUDY','weather']='CLOUDY'
df.loc[df['weather']=='LOUDY','weather']='CLOUDY'
df.loc[df['weather']=='LIHT SNOW/RAIN','weather']='LIGHT SNOW/RAIN'

df['weather'].value_counts()


# %%
# map weather to integer
map_weather = {'CLEAR': 1, 'CLOUDY': 2,'LIGHT SNOW/RAIN':3,'HEAVY SNOW/RAIN':4}
df.replace({'weather': map_weather})

# %% [markdown]
# We are set!
# %% [markdown]
# #### Task 2: Column 'guest_scooter' -- remove negative values

# %%
df['guest_scooter'].replace([-2,-1],np.nan,inplace=True)
df['guest_scooter'].describe()

# %% [markdown]
# Notice that the count has reduced. This means that some of the negative values have been converted to NULL
# %% [markdown]
# #### Task 3: Column 'relative_humidity','psi' -  value 0 should be treated as null values

# %%
df['relative_humidity'].replace(0,np.nan,inplace=True)
df['relative_humidity'].describe()


# %%
df['psi'].replace(0,np.nan,inplace=True)
df['psi'].describe()

# %% [markdown]
# #### Task 4: Column 'date' - transform to numeric data e.g. year, month, date, day of week

# %%
# first we convert the date column to date object
dt=df['date']
df['date']=pd.to_datetime(dt)


# %%
type(df['date'].values[0])

# %% [markdown]
# Now we need to create new columns and extract the year, month, date, and weekday attributes

# %%
df['year']=df['date'].dt.year
df['month']=df['date'].dt.month
df['day']=df['date'].dt.day
df['weekday']=df['date'].apply(lambda x: x.weekday())
df.head()

# %% [markdown]
# In the 'weekday' column, we notice that the number ranges from 0 to 6. We are going to add 1 to the values.

# %%
df['weekday']=df['weekday']+1
df.head()

# %% [markdown]
# We are done with preprocessing! These steps will also be performed in the data cleaning/preprocessing phase of the MLP.
# Now on to exploring some basic relationships between the attributes.
# %% [markdown]
# ## Section 4. Data Visualization
# 
# 
# Bearing in mind that the final purpose of the exercise is to predict the number of active e-scooter riders. Over here, we should try to aim to look for relationships between the other attributes with the target attribute (guest_scooters).

# %%
# first we look at the distribution of ridership/hour
plt.hist(df['guest_scooter'].dropna(),bins=50)
plt.xlabel('Number of Scooters/Hr')
plt.ylabel('Frequency')
plt.show()

# %% [markdown]
# We can see that the number of scooters/hour does not follow a normal distribution. It is heavily right-tailed.

# %%
# now we want to see if there's a longitudinal trend on daily total scooter number
group_by_day=df.groupby('date').guest_scooter.sum()
group_by_day.plot()
plt.xlabel('Date')
plt.ylabel('Daily Ridership')
plt.title("Total Number of Scooters/Day")
plt.show()

# %% [markdown]
# What we can observe from above is a clear seasonal trend: numbers spike up in horter months (May - August), and drop in colder months (Oct - Apr). There are also high variations across days

# %%
# we can see the seasonal trends more clearly if we plot the total number of riders per month
group_by_month=df.groupby('month').guest_scooter.sum()
group_by_month.plot(kind='bar')
plt.xlabel('Month')
plt.ylabel('Scooter Number')
plt.title("Total number of scooters in each month over the study period")
plt.show()


# %%

sns.heatmap(pd.crosstab(df['month'],df['hr'],values=df['guest_scooter'],aggfunc='mean'),cmap='coolwarm')
plt.ylabel("Month")
plt.xlabel("Hour of day")
plt.title("Mean hourly scooters per hour")


# %%



# %%
sns.boxenplot(data=df, x="month",y="guest_scooter")
plt.title("Distribution of guest scooter numbers across months")
plt.show()

# %% [markdown]
# The number of scooters shows clear monthly and daily variations.
# What actually makes a difference in the different months and hours is the climatic conditions, this means:
# - temperature
# - feels_like_temperature
# - relative_humidity
# - psi
# - windspeed
# - weather
# 
# All these conditions will have some influence in the result. What is interesting from the boxenplot above is also that there are two peaks/maximum hourly ridership in a year, one in March-May, the other in September - November. Now we know that Summer is usually the hottest time of a year -- we are talking about temperature here. If so, it looks like other factors e.g. thermal comfort, wind, and humidity might have an effect to scooters too. We will look at this in detail.
# %% [markdown]
# Before we drill in on the climatic factors, there is another temporal scale we have not explored: variations in a day.

# %%
# resample by hour of day
mean_rider_by_hr = df.groupby('hr')['guest_scooter'].mean().sort_index()
mean_temp_by_hr = df.groupby('hr')['temperature'].mean().sort_index()
mean_fltemp_by_hr=df.groupby('hr')['feels_like_temperature'].mean().sort_index()
mean_psi_by_hr=df.groupby('hr')['psi'].mean().sort_index()
mean_rh_by_hr=df.groupby('hr')['relative_humidity'].mean().sort_index()
mean_windspeed_by_hr=df.groupby('hr')['windspeed'].mean().sort_index()


# %%
# merge into a new dataframe
frame={'rider':mean_rider_by_hr,
      'temp':mean_temp_by_hr,
      'fltemp':mean_fltemp_by_hr,
      'psi':mean_psi_by_hr,
      'rh':mean_rh_by_hr,
      'windspeed':mean_windspeed_by_hr}
df_by_hr=pd.DataFrame(frame)
df_by_hr.head()


# %%
# plot the variables to 4 subplots
fig,ax=plt.subplots(2,2)
fig.tight_layout(pad=0.4, w_pad=6, h_pad=2.0)

ax[0,0].bar(df_by_hr.index,df_by_hr['rider'],alpha=0.2,color='grey')
ax2=ax[0,0].twinx()
ax2.plot(df_by_hr.index,df_by_hr['temp'],color='r')
ax2.plot(df_by_hr.index,df_by_hr['fltemp'],color='orange')
ax[0,0].set_ylabel('Mean Hourly Ridership')
ax2.set_ylabel("Temperature/Feels_like_temperature")
plt.legend(['Temperature','Feels_like_Temperature'])

ax[0,1].bar(df_by_hr.index,df_by_hr['rider'],alpha=0.2,color='grey')
ax3=ax[0,1].twinx()
ax3.plot(df_by_hr.index,df_by_hr['windspeed'],color='maroon')
ax[0,1].set_ylabel('Mean Hourly Ridership')
ax3.set_ylabel("Windspeed")
plt.legend(['Windspeed'])

ax[1,0].bar(df_by_hr.index,df_by_hr['rider'],alpha=0.2,color='grey')
ax4=ax[1,0].twinx()
ax4.plot(df_by_hr.index,df_by_hr['rh'],color='green')
ax[1,0].set_ylabel('Mean Hourly Ridership')
ax4.set_ylabel('Relative Humidity')
plt.legend(['Relative Humidity'])

ax[1,1].bar(df_by_hr.index,df_by_hr['rider'],alpha=0.2,color='grey')
ax5=ax[1,1].twinx()
ax5.plot(df_by_hr.index,df_by_hr['psi'],color='blue')
ax[1,1].set_ylabel('Mean Hourly Ridership')
ax5.set_ylabel("PSI")
plt.legend(['PSI'])

plt.show()

# %% [markdown]
# We can observe from the above that the shape of the hourly scooters follow windspeed most strongly, to a lesser extent, the temperature and feels_like_temperature. PSI does no seem a strong explanatory variable while relative humidity has a negative relationship.
# 
# The exact influence of each factor may vary in different seasons.
# %% [markdown]
# We want to create the same graphs as above, but this time, split them into seasons. This time we will narrow down to only temperature and windspeed.
# We will split the months into:
# - spring: Mar, Apr, May
# - summer: June, July, Aug
# - fall: Sept, Oct, Nov
# - winter: Dec, Jan, Feb

# %%
# create a new column 'Season' and do the mapping by months
df['season']=df['month']


# %%
# map month into season
df['season'].replace([3,4,5],'Spring',inplace=True)
df['season'].replace([6,7,8],'Summer',inplace=True)
df['season'].replace([9,10,11],'Fall',inplace=True)
df['season'].replace([12,1,2],'Winter',inplace=True)


# %%
df.head()


# %%
df['season'].replace('Spring',1,inplace=True)
df['season'].replace('Summer',2,inplace=True)
df['season'].replace('Fall',3,inplace=True)
df['season'].replace('Winter',4,inplace=True)
df.head()


# %%
# how does temperature affect the ridership in different seasons?
sns.relplot(x="temperature",y="guest_scooter",data=df,kind="line",hue="season",alpha=0.3,palette='Set1',legend=False)
sns.set_style("white")
plt.title("Temperature vs Hourly Scooters")
plt.xlabel("Temperature")
plt.ylabel("Hourly Scooters")
plt.legend(['Spring','Summer','Fall','Winter'])
plt.show()


# %%
# how does temperature affect the ridership in different seasons?
sns.relplot(x="relative_humidity",y="guest_scooter",data=df,kind="line",hue="season",alpha=0.3,palette='Set1',legend=False)
sns.set_style("white")
plt.title("Relative Humidity vs Hourly Scooters")
plt.xlabel("Relative Humidity")
plt.ylabel("Hourly Scooters")
plt.legend(['Spring','Summer','Fall','Winter'])
plt.show()


# %%
# how does temperature affect the ridership in different seasons?
sns.relplot(x="windspeed",y="guest_scooter",data=df,kind="line",hue="season",alpha=0.3,palette='Set1',legend=False)
sns.set_style("white")
plt.title("Windspeed vs Hourly Scooters")
plt.xlabel("Windspeed")
plt.ylabel("Hourly Scooters")
plt.legend(['Spring','Summer','Fall','Winter'])
plt.show()


# %%
# how does temperature affect the ridership in different seasons?
sns.relplot(x="feels_like_temperature",y="guest_scooter",data=df,kind="line",hue="season",alpha=0.3,palette='Set1',legend=False)
sns.set_style("white")
plt.title("Feels_Like_Temperature vs Hourly Scooters")
plt.xlabel("Windspeed")
plt.ylabel("Hourly Scooters")
plt.legend(['Spring','Summer','Fall','Winter'])
plt.show()

# %% [markdown]
# ## Section 5. Conclusion
# %% [markdown]
# After thie exercise, we have come to the understanding of:
# - the basic structure of this dataset, e.g. the target feature, 'guest_scooter', is a continuous numeric feature. This will help us choose hte suitable models in our Machine Learning Pipeline later.
# - the preprocessing steps required on this dataset
# - Several attributes that might have strong influence on the number of scooters, especially hour of day, month/season, temperature, relative_humidity, and windspeed
# 
# All these will come in handy when we build the Machine Learning Pipeline for predicting the scooter numbers.

