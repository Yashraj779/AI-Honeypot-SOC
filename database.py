from pymongo import MongoClient
from config import Config

client = MongoClient(
    Config.MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client[Config.DATABASE_NAME]

logs_collection = db[Config.LOG_COLLECTION]