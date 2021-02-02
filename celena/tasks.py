from celena.celery_app import tasker
from database import DBClient
from feeds import EarthquakeFeeds

feed = EarthquakeFeeds(DBClient())
# @tasker.task
# def add(x, y):
#     return x + y
#
#
# @tasker.task
# def mul(x, y):
#     return x * y
#
#
# @tasker.task
# def populate_


@tasker.task(rate_limit='1/m')
def earthquakes():
    print("Fetching Earthquakes from NCS")
    ncs_earthquakes = feed.get_earthquakes_ncs()
    feed.record_ncs_earthquakes(ncs_earthquakes)


# @tasker.on_after_configure.connect
# def schedule_regular_tasks(sender, **kwargs):
#     sender.add_periodic_task(
#         crontab(minute='*/2'), feed.get_earthquakes(),
#     )
