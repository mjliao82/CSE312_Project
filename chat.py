import html
from pymongo import MongoClient
import uuid


mongo_client = MongoClient("mongo")
db = mongo_client["cse312_group"]
chat_collection = db["chat"]


def postmsg(lis):
    mydic = {"username": lis[0], "message": lis[1],"id":str(uuid.uuid4())}
    chat_collection.insert_one(mydic)
    return

def getmsg():
    data = chat_collection.find({})
    container = []
    for i in data:
        i.pop('_id', None)
        container.append(i)
    return container

