from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Slack Scheduler'


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
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
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

def display_todays_events(service,now):
    #Display the events for the current day, if they exist
    today = datetime.date.today()
    midnight = datetime.datetime.combine(today, datetime.time.max)
    midnight = midnight.isoformat() + 'Z'
    todaysResults = service.events().list(
            calendarId='primary', timeMin=now, orderBy='startTime', singleEvents=True,
            timeMax=midnight).execute()
    todays_events = todaysResults.get('items',[])

    if not todays_events:
        print('No events scheduled for today')
    for event in todays_events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
        
def display_week_events(service, now):
    #Display the events from the curent day until the end of the week(Sunday), if they exist
    today = datetime.datetime.today()
    weekday = today.isoweekday();
    this_sunday = today + datetime.timedelta(days= 7 - weekday)
    this_sunday = this_sunday.isoformat() + 'Z'

    weekResults = service.events().list(
            calendarId='primary', timeMin=now, orderBy='startTime', singleEvents=True,
            timeMax=this_sunday).execute()
    week_events = weekResults.get('items',[])

    if not week_events:
        print('No events scheduled for this week')
    for event in week_events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
        
def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

if __name__ == '__main__':
    main()
