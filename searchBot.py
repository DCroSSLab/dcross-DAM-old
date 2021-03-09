import tweepy
import time

consumer_key = "NbDMP0SS5i5qbNjwVnsdynz4g"
consumer_secret = "YyzHnsA007JSngJLPQLqwV6f7InQ7eEwePcp0MIfXCg1TEaGSN"
key = "1360094602234122242-yIj9rcks2Q7VbMW4e6TKiEkj4Iu7oi"
secret = "N0L4BmeWfOS1jf1aWyHsGzXu8rxvBP1a3FGaSGBLBxdpi"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)

api = tweepy.API(auth)

hashtag = "#DCROSS"
tweetNumber = 10

tweets = tweepy.Cursor(api.search, hashtag).items(tweetNumber)


def searchBot():
    for tweet in tweets:
        try:
            tweet.retweet()
            print("Retweet Done!!")
            time.sleep(2)
        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(2)


searchBot()