import datetime
import json
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
            lat_long = earthquake['lat_long'].split(', ')
            # latitude = float(earthquake['lat_long'][:5])
            # longitude = float(earthquake['lat_long'][7:])
            latitude = float(lat_long[0])
            longitude = float(lat_long[1])
            mag_depth = earthquake['magnitude_depth']
            magnitude = float(re.search(r"\d+\.?\d*", mag_depth).group())
            depth = float(re.search(r"(\d*\.?\d*)km", mag_depth).group(1))
            # magnitude = float(mag_depth[0].replace('M: ', ''))
            # depth_string = mag_depth[1].replace('D: ', '')
            # depth = float(depth_string.replace('km', ''))
            # magnitude is type converted to float,
            # look into type converting depth to json structure like value, unit - DONE!
            name = re.sub(r'M:\s(\d+\.\d+)\s-\s', '', earthquake['event_name'])
            event = dict(type="Feature", geometry=dict(type="Point", coordinates=[longitude, latitude]),
                         properties=dict(disaster_id=ObjectId(), disaster_type="earthquake", time=time, name=name,
                                         magnitude=float(magnitude), depth=dict(value=depth, unit="km"),
                                         total_reports=0, reports=[], source="NCS", ncs_id=event_id))
            # print(event)
            # break
            disasters.insert_one(event)

    # @tasker.task
    # def get_earthquakes(self):
    #     print(datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
    #     earthquakes = self.get_earthquakes_ncs()
    #     self.record_ncs_earthquakes(earthquakes)


feed = EarthquakeFeeds(DBClient())
earthquakes = feed.get_earthquakes_ncs(days="30")
feed.record_ncs_earthquakes(earthquakes)


class IMDNowcastFeed:
    def __init__(self, client):
        self.conn = client
        self.nowcasts = client.events.nowcasts

    def get_mausam(self):
        nowcasts = self.nowcasts
        url = 'https://mausam.imd.gov.in/imd_latest/contents/stationwise-nowcast-warning.php'
        page = requests.get(url)
        soup = BeautifulSoup(page.content, features='html.parser')
        test = soup.find('script', {'type': 'text/javascript'})
        pattern = re.compile(r"\s+countrydataprovider\s+=\s+(\{.*?\});\n", flags=re.DOTALL)
        data = re.findall(pattern, test.string)
        data_fix = re.sub("([A-Za-z]+),", r'"\1",', data[0])
        data_fix = re.sub("([A-za-z]+) :", r'"\1" :', data_fix)
        data_json = json.loads(data_fix)
        count = 0
        # pprint(data_json['images'])
        indian = pytz.timezone('Asia/Kolkata')
        for forecast in data_json['images']:
            if '<p>No Warning ' in forecast['description']:
                # print(forecast['description'])
                continue
            if forecast['description'] == 'No data Available':
                continue
            # print(forecast['description'])
            station = forecast['title']
            longitude = float(forecast['longitude'])
            latitude = float(forecast['latitude'])
            date = re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}", forecast['description']).group()
            # print(date)
            # times = re.search("[0-9]{4} Hrs", forecast['description'])
            # issue_time = times.group(1)[:4]
            # expire_time = times.group(2)[:4]
            issue_time = date + ' ' + re.search("</br>[0-9]{4} Hrs</br>", forecast['description']).group()[5:9:1]
            expire_time = date + ' ' + re.search("Valid upto: [0-9]{4} Hrs", forecast['description']).group()[12:16:1]
            # issue_time -----> </br>2200 Hrs</br>  expire_time----->Valid upto: 0100 Hrs
            # print(issue_time, expire_time)
            naive_issue = datetime.datetime.strptime(issue_time, '%Y-%m-%d %H%M')
            naive_expire = datetime.datetime.strptime(expire_time, '%Y-%m-%d %H%M')
            issue_time = indian.localize(naive_issue)
            expire_time = indian.localize(naive_expire)
            exists = nowcasts.find_one({'properties.issue_time': issue_time})
            if exists:
                print("already exists!")
                continue
            # Remove all HTML tags, mainly <p>, </p> and </br> are present
            dump = re.sub("<\/?[^><]+>", '', forecast['description'])
            forecast_text = re.sub("( ? Time of issue: .*)", '', dump)
            load = {'type': "Feature", 'geometry': {'type': "Point", 'coordinates': [longitude, latitude]},
                    'properties': {'forecast_id': ObjectId(), 'forecast_type': "weather_nowcast", 'source': "IMD",
                                   'station_name': station, 'station_type': "IMD-Station",
                                   'forecast': {'description': forecast_text, 'issue_time': issue_time,
                                                'expire_time': expire_time}}}
            nowcasts.insert_one(load)


feed = IMDNowcastFeed(DBClient())
feed.get_mausam()
