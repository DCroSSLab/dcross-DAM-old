import location as location
import tweepy
import time
from Twitterfeed import collection

consumer_key = "NbDMP0SS5i5qbNjwVnsdynz4g"
consumer_secret = "YyzHnsA007JSngJLPQLqwV6f7InQ7eEwePcp0MIfXCg1TEaGSN"
key = "1360094602234122242-yIj9rcks2Q7VbMW4e6TKiEkj4Iu7oi"
secret = "N0L4BmeWfOS1jf1aWyHsGzXu8rxvBP1a3FGaSGBLBxdpi"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)

api = tweepy.API(auth)

FILE_NAME = 'last_seen.txt'


def read_last_seen(FILE_NAME):
    file_read = open(FILE_NAME, 'r')
    last_seen_id = int(file_read.read().strip())
    file_read.close()
    return last_seen_id


def store_last_seen(FILE_NAME, last_seen_id):
    file_write = open(FILE_NAME, 'w')
    file_write.write(str(last_seen_id))
    file_write.close()
    return


def reply():
    tweets = api.mentions_timeline(read_last_seen(FILE_NAME), tweet_mode='extended')
    for tweet in reversed(tweets):
        print(str(tweet.id) + ' - ' + tweet.full_text)

        if '#dcross' in tweet.full_text.lower():
            print(tweet.full_text)
            print(tweet.place)
            api.update_status("@" + tweet.user.screen_name + " Dcross Team is reporting live", tweet.id)
            store_last_seen(FILE_NAME, tweet.id)
            api.create_favorite(tweet.id)
            store_last_seen(FILE_NAME, tweet.id)

            users = api.get_user(tweet.user.screen_name)
            locations = users.location
            if locations == "":
                print("The user has not mentioned their location.")
            else:
                print("The location of the user is : " + locations)

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
                        "text": tweet.full_text,
                        "images": []
                    },
                    "is_spam": False,
                    "is_removed": False
                }
            }

            collection.insert_one(post)


while True:
    reply()
    time.sleep(2)
