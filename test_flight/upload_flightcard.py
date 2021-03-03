#!/usr/bin/python

# SEE THIS GUIDE FOR OBTAINING A GOOGLE SHEETS API KEY: https://developers.google.com/sheets/api/quickstart/python

import httplib2
import os
import sys

from datetime import datetime
from dateutil.parser import parse

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'
FIELDS = ['date','airframe', 'start_time','wind_speed','wind_direction','length','manual_time','2-cell_before','6-cell_before','9-cell_before','2-cell_after','6-cell_after','9-cell_after','waypoints','avg._min_dist','flight_notes']


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
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def update_spreadsheet(filename):
    cards = []
    with open(filename, 'r') as f:
        cards = [[element.strip() for element in line.strip().split(",")] for line in f.readlines()]
    for line in cards:
        # make sure there are the right number of fields. maybe python's csv would work better
        assert len(line) == len(FIELDS), "Error: length of fields is {} should be {}".format(len(line), len(FIELDS))
    cards = cards[1:]  # skip header line

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '134aaYnT1QtmNhBQ4Sp_wPSAmpsGMJLQFk6lvjvtWwm4'
    rangeName = 'MainSheet!A:P'
    values = cards
    body = {'values': values}
    vauleInputOption = "RAW"

    request = service.spreadsheets().values().append(spreadsheetId=spreadsheetId, valueInputOption=vauleInputOption,
                                                     range=rangeName, body=body)
    response = request.execute()
    print(response)


def main():
    if len(sys.argv) != 2:
        print("upload_flightcard: No filename specified\nUsage: upload_flightcard.py <filename.csv>")
        sys.exit(1)

    update_spreadsheet(sys.argv[1])


if __name__ == '__main__':
    main()
