import html
from pymongo import MongoClient


mongo_client = MongoClient("mongo")
db = mongo_client["cse312_group"]
chat_collection = db["chat"]


def postmsg(lis):
    mydic = {"username": lis[0], "message": lis[1]}
    chat_collection.insert_one(mydic)
    return

def getmsg():
    data = chat_collection.find({})
    container = []
    for i in data:
        i.pop('_id', None)
        container.append(i)
    return container