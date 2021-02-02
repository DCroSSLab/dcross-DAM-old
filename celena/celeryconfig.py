broker = 'amqp://guest@localhost:5672/'
# result_backend = 'mongodb://faraaz@winterfell/localhost:27017/celery_results'
result_backend = 'mongodb://faraaz:winterfell@localhost:27017/?authSource=admin&authMechanism=SCRAM-SHA-256'
# see firefox bookmark under eyic/celeery and fix the result backend
mongodb_backend_settings = {
    'database': 'celery_results',
    'taskmeta_collection': 'celery_taskmeta',
    'user': 'faraaz',
    'password': 'winterfell'}

include = ['celena.tasks']
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Kolkata'
