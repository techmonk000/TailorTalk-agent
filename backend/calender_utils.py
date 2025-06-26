from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import datetime, os, pickle

SCOPES = ['https://www.googleapis.com/auth/calendar']

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
    service = get_calendar_service()
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return len(events_result.get('items', [])) == 0

def create_event(start_time, end_time, summary="TailorTalk Call"):
    service = get_calendar_service()
    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event
