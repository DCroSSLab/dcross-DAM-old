from pymongo import MongoClient
from bson.codec_options import CodecOptions
from bson.json_util import dumps, loads
import json
from datetime import datetime, timedelta
import pytz
uri = "mongodb+srv://Saumyaranjan:mongodb@cluster0.yqomn.mongodb.net/test"


class DBClient:
    def __init__(self):
        client = MongoClient(uri)
        self.connection = client
        self.events = client.events
        # self.disasters = client.events.disasters
        # self.earthquakes = client.events.earthquakes
        # self.floods = client.events.floods
        # self.cyclones = client.events.cyclones
