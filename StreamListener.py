import tweepy
from Twitterfeed import collection

consumer_key = "zk9oBLweCS8HAVQUEaqDWFkxG"
consumer_secret = "qlnLERV1NnTgcGn9CvlBTloIXac3ciucTPwjVjPOdPrBUuSjAJ"
access_token = "1360094602234122242-lnnvTXeXHXQb4tzrvnFd02OzwTpzuO"
access_token_secret = "O5A18DLGGPr5rsxPXDzk8fQgfsyp4gSkxlYMi6LO4WK2u"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print(status)
        post = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": status.place,
                "location": status.user.location
            },
            "properties": {
                "reporter_id": "ID of new or existing user",
                "source": {
                    "platform": "Twitter",
                    "tweet_id": status.user.id_str,
                    "user_name": status.user.screen_name,
                    "user_language": status.user.lang,
                    "user_timezone": status.user.time_zone
                },
                "disaster": {
                    "type": "earthquake",
                    "_id": "Search for a disaster in db and set this id. This is like foreign key"
                },
                "description": {
                    "text": status.text,
                    "images": []
                },
                "is_spam": False,
                "is_removed": False
            }
        }

        collection.insert_one(post)

    def on_error(self, status_code):
        if status_code == 420:
            return False


def main():
    stream = tweepy.Stream(api.auth, StreamListener())
    stream.filter(track=["Earthquake"])


if __name__ == "__main__":
    main()
