# from celena import celeryconfig
from celery import Celery
from celery.schedules import crontab

# tasker = Celery('proj',
#                 broker='pyamqp://guest@localhost//',
#                 result_backend='mongodb://faraaz:winterfell@localhost:27017/'
#                                '?authSource=admin&authMechanism=SCRAM-SHA-256',
#                 mongodb_backend_settings={
#                     'database': 'celery_results'},
#                 include=['proj.tasks'])
tasker = Celery('celena')
tasker.config_from_object('celena.celeryconfig')

# Optional configuration, see the application user guide.
tasker.conf.update(
    result_expires=3600,
)
tasker.conf.beat_schedule = {
    'earthquake-every-5-minutes': {
        'task': 'celena.tasks.earthquakes',
        'schedule': crontab(minute='*/5')
    },
    'nowcasts-every-5-minutes': {
        'task': 'celena.tasks.nowcasts',
        'schedule': crontab(minute='*/5')
    }
}
tasker.conf.timezone = 'UTC'

if __name__ == '__main__':
    tasker.start()
