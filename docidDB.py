import json
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.test_database
collection = db.urlIndex

d = {}
with open('bookkeeping.json', 'r') as f:
    data = json.load(f)
for eachname in data.keys():
    arr = eachname.split('/')
    folder = int(arr[0])
    id = int(arr[1])
    docid = folder * 500 + id
    d[docid] = data[eachname]

for key in d.keys():
    record = {}
    record['id'] = key
    record['url'] = d[key]
    collection.insert_one(record)
#with open("idToUrl.json", 'w') as ff:
    #json.dump(d, ff, indent = 2)

