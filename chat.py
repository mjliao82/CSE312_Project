import html
from pymongo import MongoClient


mongo_client = MongoClient("mongo")
db = mongo_client["cse312_group"]
chat_collection = db["chat"]