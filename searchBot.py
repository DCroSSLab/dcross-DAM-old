import tweepy
from Twitterfeed import collection

consumer_key = "zk9oBLweCS8HAVQUEaqDWFkxG"
consumer_secret = "qlnLERV1NnTgcGn9CvlBTloIXac3ciucTPwjVjPOdPrBUuSjAJ"
key = "1360094602234122242-lnnvTXeXHXQb4tzrvnFd02OzwTpzuO"
secret = "O5A18DLGGPr5rsxPXDzk8fQgfsyp4gSkxlYMi6LO4WK2u"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)

api = tweepy.API(auth)

hashtag = ["#FLOOD" or "#ASSAM" or "#assamflood"]
tweetNumber = 3

tweets = tweepy.Cursor(api.search, hashtag).items(tweetNumber)


def searchBot():
    for tweet in tweets:
        print(tweet.text)
        post = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": tweet.place
            },
            "properties": {
                "reporter_id": "ID of new or existing user",
                "source": {
                    "platform": "Twitter",
                    "tweet_id": tweet.id,
                    "user_name": tweet.user.screen_name
                },
                "disaster": {
                    "type": "earthquake",
                    "_id": "Search for a disaster in db and set this id. This is like foreign key"
                },
                "description": {
                    "text": tweet.text,
                    "images": []
                },
                "is_spam": False,
                "is_removed": False
            }
        }

        collection.insert_one(post)


searchBot()
