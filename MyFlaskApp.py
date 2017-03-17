import os
import flask
import httplib2
from apiclient import discovery
from apiclient.http import MediaIoBaseDownload, MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from pymongo import MongoClient
import gridfs
import last_update
import io
import datetime



app = flask.Flask(__name__)

mongoclient = MongoClient()
db = mongoclient.drive_backup
coll = db.dataset
fs=gridfs.GridFS(db)


@app.route('/')
def index():
    credentials = get_credentials()
    if credentials == False:
        return flask.redirect(flask.url_for('oauth2callback'))
    elif credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        print('now synchronizing')
        synchronize()


@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets('client_secret.json',
                                          scope='https://www.googleapis.com/auth/drive',
                                          redirect_uri=flask.url_for('oauth2callback',
                                                                     _external=True))  # access drive api using developer credentials
    flow.params['include_granted_scopes'] = 'true'
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        open('credentials.json', 'w').write(credentials.to_json())  # write access token to credentials.json locally
        return flask.redirect(flask.url_for('index'))


def get_credentials():
    credential_path = 'credentials.json'

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        print("Credentials not found.")
        return False
    else:
        print("Credentials fetched successfully.")
        return credentials


def synchronize():

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
    page_token=None

    while True:

        response = drive_service.files().list(q="(mimeType contains 'zip' "+"or mimeType contains 'pdf'"+"or mimeType co"
													"ntains 'doocx'"+"or mimeType contains 'ppot'"+"or mimeType contains "
													"'jpog'"+"or mimeType contains 'ppt'"+"or mimeType contains 'jpo"
													"g'"+"or mimeType contains 'ppot'"+"or mimeType contains 'pnog') "
													"and modifiedTime > '2012-06-04T12:00:00-08:00'",spaces='drive',fields='nextPageToken, files(id, name, modifiedTime)',pageToken=page_token).execute()

        print("********************************************************")
        print("downloading new files")
        print("********************************************************")
        files = response.get('files', [])
        if not files:
            print('No files')
        else:
            for file in files:
                drive_id = file.get('id')
                print(drive_id)
                file_name = file.get('name')
                print(file_name)
                print("modified time d'après le drive " + str(last_update.to_date(file.get('modifiedTime')))+" après parsing")
                print("modified time d'après le drive "+file.get('modifiedTime'))
                if fs.exists(metadata=drive_id, filename=file_name):
                    print('file exists')
                    fp = fs.get_last_version(metadata=drive_id)
                    print("modified time d'après mongo db "+str(fp.uploadDate))
                    if last_update.to_date(file.get('modifiedTime')) > fp.uploadDate:
                        print ('but is not up to date')
                        request = drive_service.files().get_media(fileId=drive_id)
                        fh = io.BytesIO()
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            print('downloading')
                            status, done = downloader.next_chunk()
                        fs.delete(fp._id)
                        fs.put(fh.getvalue(), filename=file_name,metadata=drive_id)

                    else:
                        print("the file "+file_name+" is already in mongodb database")
                else:
                    'file doesnt exist'
                    request = drive_service.files().get_media(fileId=drive_id)
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print('downloading')

                    fs.put(fh.getvalue(), filename=file_name, metadata=drive_id)

        if page_token is None:
            break;



if __name__ == '__main__':
    if os.path.exists('client_secret.json') == False:
        print('Client secrets file (client_id.json) not found in the app path.')
        exit()
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.run(debug=True)