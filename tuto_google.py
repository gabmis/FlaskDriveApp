from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import io
from apiclient.http import MediaIoBaseDownload
import last_update

from pymongo import MongoClient
import gridfs
import os
from oauth2client.file import Storage




try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)

    results = drive_service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))

    page_token = None

    db = MongoClient().gridfs_example
    fs = gridfs.GridFS(db)

    while True:
        date_of_last_pull = last_update.get()
        #print(date_of_last_pull)



        response = drive_service.files().list(q="(mimeType contains 'xlxs' "+"or mimeType contains 'png') and modifiedTime > '2012-06-04T12:00:00-08:00'",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()

        last_update.update()
        print("********************************************************")
        print("downloading new files")
        print("********************************************************")
        files = response.get('files', [])
        if not files:
            print('No files')
        else:
            for file in files:
                file_id = file.get('id')
                print(file_id)
                file_name = file.get('name')
                print(file_name)
                if fs.exists(filename=file_name):
                    print("the file "+file_name+" is already in mongodb database")
                else:
                    request = drive_service.files().get_media(fileId=file_id)
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()

                    oid = fs.put(fh, filename=file_name, id=file_id)

                    file_from_db = fs.get(oid)
                    print(file_from_db.filename)

        page_token = response.get('nextPageToken', None)

        if page_token is None:
            break;



if __name__ == '__main__':
    main()
    main()

