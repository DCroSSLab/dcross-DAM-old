from database import DBClient

db = DBClient()
disasters = db.events.disasters
# 0.089992801
earthquakes_near_user = disasters.find({"geometry": {"$within": {"$center": [[72.814065, 19.370594], 0.0089992801]}}})

# for eq in earthquakes_near_user:
#     print(eq)