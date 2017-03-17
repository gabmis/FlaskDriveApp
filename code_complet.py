from __future__ import print_function
import httplib2
import os

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import io
from googleapiclient.http import MediaIoBaseDownload
import last_update

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API tuto_google'


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
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)

    page_token = None



    while True:
        date_of_last_pull = last_update.get()



        response = drive_service.files().list(q="(mimeType contains 'pdf' or mimeType contains 'ppt' or mimeType contains 'pptx) and modifiedTime>%d'",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()

        last_update.update()

        for file in response.get('files', []):
            # Process change
            print
            'Found file: %s (%s)' % (file.get('name'), file.get('id'))
            file_id = file.get('id')
            request = drive_service.files().get_media(fileId=file_id)
            #fh = io.BytesIO()
            fh = io.FileIO()
            #fh = io.FileIO('cow.png', mode='wb') peut etre plus approprié ici
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print
                "Download %d%%." % int(status.progress() * 100)

            if fh.__sizeof__()>1000:


        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break;


if __name__ == '__main__':
    main()

