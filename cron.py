from feeds import EarthquakeFeeds
from database import DBClient
import requests
from bs4 import BeautifulSoup
import re
from pyjsparser import parse
import json
from pprint import pprint
from bson.objectid import ObjectId
import pytz
import datetime
# from slimit.parser import Parser
# from slimit.visitors import nodevisitor
# from slimit import ast
# client = DBClient()
# feeder = EarthquakeFeeds(client)
#
# eqs = feeder.get_earthquakes_ncs(days="1")
# feeder.record_ncs_earthquakes(eqs)
def get_storms_nwp():
    url = 'https://nwp.imd.gov.in/ts/data.php'
    data = requests.get(url)
    # print(data.content)
    soup = BeautifulSoup(data.content, features='html.parser')
    for noodle in soup.markers:
        print(noodle)
        name = noodle['name']
        message = noodle['msg']
        warning = noodle['warning']
        issue_time = noodle['timeissue']
        longitude = noodle['lng']
        latitude = noodle['lat']
        report = dict(type="Feature", geometry=dict(type="Point", coordinates=[longitude, latitude]),
                      properties=dict(forecast_id = ObjectId(), forecast_type=""))
        # print(name)

def get_mausam():
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
        longitude = forecast['longitude']
        latitude = forecast['latitude']
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
        # Remove all HTML tags, mainly <p>, </p> and </br> are present
        dump = re.sub("<\/?[^><]+>", '', forecast['description'])
        forecast_text = re.sub("( ? Time of issue: .*)", '', dump)
        load = {'type': "Feature", 'geometry': {'type': "Point", 'coordinates': [longitude, latitude]},
                'properties': {'forecast_id': ObjectId(), 'forecast_type': "weather_nowcast", 'source': "IMD",
                               'station_name': station, 'station_type': "IMD-Station",
                               'forecast': {'description': forecast_text, 'issue_time': issue_time,
                                            'expire_time': expire_time}}}
        # print(load)


def get_stations():
    types = ['ARG', 'AWS', 'AGRO']
    station_type = 'AWS'
    networks = ('http://aws.imd.gov.in:8091/AWS/network.php?a={}').format(station_type)
    print(networks)
    data = requests.get(networks)
    for item in data.json():
        latitude = item[0]
        longitude = item[1]
        state = item[3]
        district = item[4]
        station_name = item[5]
        station = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [longitude, latitude]},
                   'properties': {'name': station_name, 'district': district, 'state': state, 'type': 'AWS'},
                   'forecasts': {}}


# def get_rain_weather():
#     networks = ('http://aws.imd.gov.in:8091/AWS/network.php?a={}').format(station_type)
# http://aws.imd.gov.in:8091/AWS/dataonmap.php?a=AWSAGRO&b=2020-11-03&c=0
# a is station type- can be AWS, ARG, ARGO, AWSAGRO; b is date- can be of the last 8 days;
# c is time in hours in UTC
#     url = 'http://aws.imd.gov.in:8091/AWS/dataonmap.php?a=ALL&b=2020-10-31&c=0'
#     data = requests.get(url)
#     print(type(data))
#     for cast in data.json():
#         latitude =


# replace_test()
get_stations()
