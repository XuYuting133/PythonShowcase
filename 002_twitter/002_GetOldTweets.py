#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      ytxu
#
# Created:     01/09/2020
# Copyright:   (c) ytxu 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

consumer_key= ''
consumer_secret= ''
access_token= ''
access_token_secret= ''

import sys
if sys.version_info[0] < 3:
    import got
else:
    import got3 as got

def printTweet(descr, t):
	print(descr)
	print("Username: %s" % t.username)
	print("Retweets: %d" % t.retweets)
	print("Text: %s" % t.text)
	print("Mentions: %s" % t.mentions)
	print("Hashtags: %s\n" % t.hashtags)

tweetCriteria = got.manager.TweetCriteria().setUsername('barackobama').setMaxTweets(1)
tweet = got.manager.TweetManager.getTweets(tweetCriteria)[0]

tweetCriteria = got.manager.TweetCriteria().setUsername("barackobama").setSince("2019-09-10").setUntil("2020-08-12").setMaxTweets(3)
tweet = got.manager.TweetManager.getTweets(tweetCriteria)[1]
