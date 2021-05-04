#!/usr/bin/env python
# coding: utf-8

# In[5]:


import tweepy, datetime
import json, os, sys
from pymongo import MongoClient

folderPath = r"C:\Users\ytxu\Documents\GE5228\Data Collection"

def WriteTweetToFile(status):

    today_str = datetime.date.today().strftime("%Y%m%d")
    dataFileName = "test_new.txt"
    #dataFileName = "StreamedTweet_{}.txt".format(today_str)
    dataFilePath = os.path.join(folderPath, dataFileName)
    if not os.path.exists(dataFilePath):
        csvFile = open(dataFilePath,"a",encoding="utf-8")
        csvFile.write("Created_At|Tweet_ID|Truncated|Text|Source|Source_URL|User_Name|")
        csvFile.write("User_Screen_Name|User_Location|Tweet_Coordinates_Type|Longitude|Latitude|Place_ID|Place_URL|Place_Type|")
        csvFile.write("Place_Name|Place_Full_Name|Place_Country|Place_BoundingBox_Coordinates|Place_BoundingBox_Type|Place_Attributes|")
        csvFile.write("Language|Timestamp_MS\n")
        csvFile.close()

    csvFile = open(dataFilePath,"a",encoding="utf-8")
    csvFile.write(str(status.created_at + datetime.timedelta(hours=8))+"|") # convert UTC time to UTC+8
    csvFile.write(status.id_str+"|")
    csvFile.write(str(status.truncated)+"|")
    csvFile.write(status.text.replace("|","").replace("\n","")+"|")
    csvFile.write(status.source+"|")
    csvFile.write(status.source_url+"|")
    csvFile.write(status.user.name+"|")
    csvFile.write(status.user.screen_name+"|")
    csvFile.write(str(status.user.location)+"|")
    #csvFile.write(str(status.geo)+"|")
    if status.coordinates is not None:
        csvFile.write(str(status.coordinates['type'])+"|")
        csvFile.write(str(status.coordinates['coordinates'][0])+"|") # longitude
        csvFile.write(str(status.coordinates['coordinates'][1])+"|") # latitude
    else:
        csvFile.write("None|None|None|")
    csvFile.write(str(status.place.id)+"|")
    csvFile.write(str(status.place.url)+"|")
    csvFile.write(str(status.place.place_type)+"|")
    csvFile.write(str(status.place.name)+"|")
    csvFile.write(str(status.place.full_name)+"|")
    csvFile.write(str(status.place.country)+"|")
    csvFile.write(str(status.place.bounding_box.coordinates)+"|")
    csvFile.write(str(status.place.bounding_box.type)+"|")
    csvFile.write(str(status.place.attributes)+"|")
    csvFile.write(str(status.lang)+"|")
    csvFile.write(str(status.timestamp_ms)+"|")
    csvFile.write("\n")

    csvFile.close()

class StreamListener(tweepy.StreamListener):
    """tweepy.StreamListener is a class provided by tweepy used to access
    the Twitter Streaming API to collect tweets in real-time.
    """

    def on_connect(self):
        """Called when the connection is made"""

        print("You're connected to the streaming server.")

    def on_error(self, status_code):
        """This is called when an error occurs"""

        print('Error: ' + repr(status_code))
        return False

    def on_status(self,status):
        #if status.lang =='en':
        WriteTweetToFile(status)
            #csvFile.write(str(status.created_at))
            #csvFile.write("|")
            #csvFile.write(str(status.user.name))
            #csvFile.write("|")
            #csvFile.write(str(status.text))
            #csvFile.write("|")
            #csvFile.write(str(status.geo))
            #csvFile.write("\n")


if __name__ == "__main__":

    # These are provided to you through the Twitter API after you create a account
    consumer_key= 'shaiv6y1pCmaPjSsdhm4bgsQk'
    consumer_secret= 'KwxcACT8kkjzSZBOcR7TJtowb0vBkauulBZmStMZ2JVjcycel4'
    access_token= '952001063711723520-EBcsY6meCRiVhmLcKa11KBDYPN38hR4'
    access_token_secret= 'z988tNAU51vwokQOwW4xLEYVFpzf57NUSqoyJw55vyT2j'

    auth1 = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth1.set_access_token(access_token, access_token_secret)

    # LOCATIONS are the longitude, latitude coordinate corners for a box that restricts the
    # geographic area from which you will stream tweets. The first two define the southwest
    # corner of the box and the second two define the northeast corner of the box.
    LOCATIONS = [103.585588, 1.197221, 104.030534, 1.477982]

    stream_listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
    stream = tweepy.Stream(auth=auth1, listener=stream_listener)
    stream.filter(locations=LOCATIONS)



