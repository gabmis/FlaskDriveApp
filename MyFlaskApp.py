import os
import flask
import httplib2
from apiclient import discovery
from apiclient.http import MediaIoBaseDownload, MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


app = flask.Flask(__name__)

@app.route('/')
def index():
	credentials = get_credentials()
	if credentials == False:
		return flask.redirect(flask.url_for('oauth2callback'))
	elif credentials.access_token_expired:
		return flask.redirect(flask.url_for('oauth2callback'))
	else:
		print('now calling fetch')
		all_files = fetch("'root' in parents and mimeType = 'application/vnd.google-apps.folder'", sort='modifiedTime desc')
		s = ""
		for file in all_files:
			s += "%s, %s<br>" % (file['name'],file['id'])
		return s

@app.route('/oauth2callback')
def oauth2callback():
	flow = client.flow_from_clientsecrets('client_id.json',
			scope='https://www.googleapis.com/auth/drive',
			redirect_uri=flask.url_for('oauth2callback', _external=True)) # access drive api using developer credentials
	flow.params['include_granted_scopes'] = 'true'
	if 'code' not in flask.request.args:
		auth_uri = flow.step1_get_authorize_url()
		return flask.redirect(auth_uri)
	else:
		auth_code = flask.request.args.get('code')
		credentials = flow.step2_exchange(auth_code)
		open('credentials.json','w').write(credentials.to_json()) # write access token to credentials.json locally
		return flask.redirect(flask.url_for('index'))