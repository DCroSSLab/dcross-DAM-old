from pymongo import MongoClient
from bson.codec_options import CodecOptions
from bson.json_util import dumps, loads
import json
from datetime import datetime, timedelta
import pytz
uri = "mongodb://faraaz:winterfell@localhost:27017/?authSource=admin&authMechanism=SCRAM-SHA-256"


class DBClient:
    def __init__(self):
        client = MongoClient(uri)
        self.connection = client
        self.events = client.events
        # self.disasters = client.events.disasters
        # self.earthquakes = client.events.earthquakes
        # self.floods = client.events.floods
        # self.cyclones = client.events.cyclones
