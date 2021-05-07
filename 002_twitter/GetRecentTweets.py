#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import tweepy as tw
import pandas as pd
import sys
import config
import datetime


# In[2]:


consumer_key= config.consumer_key
consumer_secret= config.consumer_secret
access_token= config.access_token
access_token_secret= config.access_token_secret


# In[6]:


auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)


# In[5]:


date_since = "2020-09-16"
date_until = "2020-09-17"


# In[33]:

data_file = r"data\SearchTweets_UTC_20200916.txt"
if not os.path.exists(data_file):

    write_file = open(data_file,"w",encoding='utf-8')
    write_file.write("Created_At|Tweet_ID|Truncated|Text|Source|Source_URL|User_Name|")
    write_file.write("User_Screen_Name|User_Location|Tweet_Coordinates_Type|Longitude|Latitude|Place_ID|Place_URL|Place_Type|")
    write_file.write("Place_Name|Place_Full_Name|Place_Country|Place_BoundingBox_Coordinates|Place_BoundingBox_Type|Place_Attributes|")
    write_file.write("Language|Timestamp_MS\n")
    write_file.close()


tweets = tw.Cursor(api.search,
              q="",
              geocode="1.361954,103.819259,25km",
              since=date_since,
              until=date_until).items() 

# In[34]:

total_tweets=0
w_location = 0
w_coord = 0

def WriteTweetToFile(status):
    global w_location
    global w_coord
    global total_tweets
    write_file = open(data_file,"a",encoding='utf-8')
    write_file.write(str(status.created_at + datetime.timedelta(hours=8))+"|") # convert UTC time to UTC+8
    write_file.write(status.id_str+"|")
    write_file.write(str(status.truncated)+"|")
    write_file.write(status.text.replace("|","").replace("\n","")+"|")
    write_file.write(status.source+"|")
    if status.source_url is not None:
        write_file.write(status.source_url+"|")
    else:
        write_file.write("None|")
    write_file.write(status.user.name.replace("|", " ")+"|")
    write_file.write(status.user.screen_name.replace("|"," ")+"|")
    write_file.write(str(status.user.location).replace("|"," ").replace("\n"," ")+"|")
    #write_file.write(str(status.geo)+"|")
    if status.coordinates is not None:
        write_file.write(str(status.coordinates['type'])+"|")
        write_file.write(str(status.coordinates['coordinates'][0])+"|") # longitude
        write_file.write(str(status.coordinates['coordinates'][1])+"|") # latitude
    else:
        write_file.write("None|None|None|")

    if status.place is not None:
        write_file.write(str(status.place.id)+"|")
        write_file.write(str(status.place.url)+"|")
        write_file.write(str(status.place.place_type)+"|")
        write_file.write(str(status.place.name).replace("\n"," ").replace("|"," ")+"|")
        write_file.write(str(status.place.full_name).replace("\n"," ").replace("|"," ")+"|")
        write_file.write(str(status.place.country)+"|")
        write_file.write(str(status.place.bounding_box.coordinates)+"|")
        write_file.write(str(status.place.bounding_box.type)+"|")
        write_file.write(str(status.place.attributes)+"|")
    else:
        write_file.write("None|None|None|None|None|None|None|None|None|")
    write_file.write(str(status.lang)+"|")
    #write_file.write(str(status.timestamp_ms)+"|")
    write_file.write("\n")
    print(status.created_at)

    write_file.close()

for tweet in tweets:
    total_tweets += 1
    if tweet.created_at < datetime.datetime.now().replace(day=16,hour=14,minute=25):
        WriteTweetToFile(tweet)

    if total_tweets%1000==0:
        print(total_tweets)
print("..completed")
print("Total: {}".format(total_tweets))
print("With Place Name: {}".format(w_location))
print("With coordinates: {}".format(w_coord))
print("END: "+str(datetime.datetime.now()))



