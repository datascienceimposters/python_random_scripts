#You need to configure using https://developers.google.com/gmail/api/quickstart/python#
#
from __future__ import print_function
import httplib2
import os
import base64
import email
from apiclient import errors
import ast

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


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
                                   'gmail-python-quickstart.json')

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
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().list(userId='me').execute()

    query = ''
    response = service.users().messages().list(userId='me',labelIds='SENT', q=query ).execute()
    all = []

    if 'messages' in response: 
        all.extend(response['messages'])

    while 'nextPageToken' in response:
      
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId='me',labelIds='SENT', q=query, 
                                         pageToken=page_token).execute()
        all.extend(response['messages'])

	#in order to limit the amount of processing,
	#I have limite this to 2000 entries
        if len(all) > 2000: #2000:
            print(page_token)
            break

    emails = {}
   
    #the new few lines, I only want to print the email address from the headers
    #this could be easily updated to include the number of emails received from an address 
    for m in all:
        #print(m)	
        headers = GetMessageHeaders(service, 'me', m['id'])
        for entry in headers:
            if entry['name'] == 'To':
                for address in entry['value'].split(","): 
                    emails[ address  ] = 1
        
    for email in emails:
        print( email ) 

def GetMessageHeaders(service, user_id, msg_id):
  """Get a Message and use it to create a MIME Message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A MIME Message, consisting of data from Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='metadata').execute()

    headers = message['payload']['headers'] 
    return( headers )

  except error:
    print( 'An error occurred: %s' % error)


if __name__ == '__main__':
    main()
