from pymongo import MongoClient
import gridfs
import os
from oauth2client.file import Storage
import io

#il faut d'abord lancer une session mongodb dans le shell

db = MongoClient().gridfs_example
fs = gridfs.GridFS(db)


home_dir = os.path.expanduser('~')
home_dir = os.path.join(home_dir, 'PycharmProjects')
home_dir = os.path.join(home_dir, 'avec_google')
home_dir = os.path.join(home_dir, 'photo.jpg')

store = Storage(home_dir)
photo = store.get()

fh = io.BytesIO()
file_id2 = fs.put(fh, contentType = "image/jpg")
file_id = fs.put(open("photo.jpg","rb"))

file = fs.get(file_id)
print(file.read())