import os
import datetime
import pickle
import pytz
from dateutil import parser
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']
IST = pytz.timezone("Asia/Kolkata")

def get_calendar_service():
    creds = None
    if os.path.exists('token.pkl'):
        creds = pickle.load(open("token.pkl", "rb"))
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials/credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        pickle.dump(creds, open("token.pkl", "wb"))
    return build('calendar', 'v3', credentials=creds)

def check_availability(start_time, end_time):
    start_time = IST.localize(start_time)
    end_time = IST.localize(end_time)
    service = get_calendar_service()
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    for event in events_result.get('items', []):
        existing_start = parser.parse(event['start'].get('dateTime', event['start'].get('date')))
        existing_end = parser.parse(event['end'].get('dateTime', event['end'].get('date')))
        if (start_time < existing_end) and (end_time > existing_start):
            return False
    return True

def get_upcoming_events():
    service = get_calendar_service()
    now = datetime.datetime.now(IST).isoformat()
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def get_events_on_day(date: datetime.datetime):
    date = IST.localize(date)
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + datetime.timedelta(days=1)
    service = get_calendar_service()
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def create_event(start_time, end_time, summary="TailorTalk Call"):
    start_time = IST.localize(start_time)
    end_time = IST.localize(end_time)
    service = get_calendar_service()

    existing_events = service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    for event in existing_events.get('items', []):
        event_summary = event.get('summary', '')
        existing_start = parser.parse(event['start'].get('dateTime', event['start'].get('date')))
        existing_end = parser.parse(event['end'].get('dateTime', event['end'].get('date')))
        if event_summary == summary and start_time == existing_start and end_time == existing_end:
            return {"status": "duplicate", "message": "Event already exists"}

    event_body = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
    }
    event = service.events().insert(calendarId='primary', body=event_body).execute()
    return {"status": "created", "event": event}
