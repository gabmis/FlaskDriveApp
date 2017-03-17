#une session mongod doit avoir été préalablement lancée sur le shell

from pymongo import MongoClient
import gridfs

client = MongoClient()

client = MongoClient('localhost', 27017)

db = client.test_database
#

collection = db.test_collection

import datetime

post = {"author": "Mike",
         "text": "My first blog post!",
         "tags": ["mongodb", "python", "pymongo"],
         "date": datetime.datetime.utcnow()}

posts=db.post
posts.insert_one(post)


import pprint
pprint.pprint(posts.find_one({"author": "Mike"}))

