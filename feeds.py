import datetime
import re
import pytz
import requests
from bs4 import BeautifulSoup
from bson.json_util import loads
from bson.objectid import ObjectId
from database import DBClient

# from proj.celery_app import tasker


# from pymongo import MongoClient


# client = MongoClient("mongodb://faraaz:winterfell@localhost:27017/?authSource=admin&authMechanism=SCRAM-SHA-256")


class EarthquakeFeeds:
    def __init__(self, client):
        self.conn = client
        self.disasters = client.events.disasters
        # self.earthquakes = client.events.earthquakes
        # self.hello = "hello"

    # @tasker.task
    def get_earthquakes_ncs(self, region: str = "I", north: str = "", west: str = "", east: str = "",
                            south: str = "", latitude: str = "", longitude: str = "", distance: str = "",
                            days: str = "1", start_date: str = "", end_date: str = "", mag_min: str = "0",
                            mag_max: str = "10", depth_min: str = "0", depth_max: str = "1000",
                            timezone: str = "IST"):
        url = "https://seismo.gov.in/MIS/riseq/earthquake"
        if timezone != "IST" and timezone != "UTC":
            return None
        while days not in ({"", "1", "7", "30"}):
            return None
        if north and west and south and east != "":
            region = "C"
        if start_date and end_date != "":
            days = "C"
        if timezone == "IST":
            timezone = "2"
        elif timezone == "UTC":
            timezone = "1"
        parameters = {
            "region": region,
            "region_lat_2": north,
            "region_long_1": west,
            "region_long_2": east,
            "region_lat_1": south,
            "point_lat": latitude,
            "point_long": longitude,
            "point_distance": distance,
            "days": days,
            "start_time": start_date,
            "end_time": end_date,
            "magnitude-min": mag_min,
            "magnitude-max": mag_max,
            "depth-min": depth_min,
            "depth-max": depth_max,
            "timezone": timezone,
            "submit": "Apply"
        }
        page = requests.post(url, data=parameters)
        juice = BeautifulSoup(page.content, 'html.parser')
        data = juice.find_all('li', 'list-view-item event_list')
        earthquakes = [loads(item.attrs.get('data-json')) for item in data]
        return earthquakes

    # @tasker.task
    def record_ncs_earthquakes(self, earthquakes):
        disasters = self.disasters
        indian = pytz.timezone('Asia/Kolkata')
        for earthquake in earthquakes:
            # print(earthquake)
            event_id = earthquake['event_id']
            # print(event_id)
            exists = disasters.find_one({'properties.ncs_id': event_id})
            if exists:
                print(event_id + " already exists!")
                continue
            naive = datetime.datetime.strptime(earthquake['origin_time'][:19], '%Y-%m-%d %H:%M:%S')
            time = indian.localize(naive)
            latitude = earthquake['lat_long'][:5]
            longitude = earthquake['lat_long'][7:]
            mag_depth = earthquake['magnitude_depth'].split(' - ')
            magnitude = mag_depth[0].replace('M: ', '')
            depth = mag_depth[1].replace('D: ', '')
            # magnitude is type converted to float, look into type converting depth to json structure like value, unit
            name = re.sub(r'M:\s(\d+\.\d+)\s-\s', '', earthquake['event_name'])
            event = dict(type="Feature", geometry=dict(type="Point", coordinates=[longitude, latitude]),
                         properties=dict(disaster_id=ObjectId(), disaster_type="earthquake", time=time, name=name,
                                         magnitude=float(magnitude), depth=depth, total_reports=0, reports=[],
                                         source="NCS", ncs_id=event_id))
            disasters.insert_one(event)

    # @tasker.task
    # def get_earthquakes(self):
    #     print(datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
    #     earthquakes = self.get_earthquakes_ncs()
    #     self.record_ncs_earthquakes(earthquakes)


feed = EarthquakeFeeds(DBClient())
earthquakes = feed.get_earthquakes_ncs(days="30")
feed.record_ncs_earthquakes(earthquakes)
