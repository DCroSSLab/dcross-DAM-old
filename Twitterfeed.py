from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://Saumyaranjan:mongodb@cluster0.yqomn.mongodb.net/test")
db = cluster["Reports"]
collection = db["TwitterReports"]

