import os
import requests
from datetime import datetime, timedelta
from dateutil import parser
from backend.calender_utils import (
    check_availability,
    create_event,
    get_upcoming_events,
    get_events_on_day,
)
from dotenv import load_dotenv

load_dotenv()

def call_llm(prompt: str):
    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1",
                "prompt": prompt,
                "stream": False
            }
        )
        data = res.json()
        print("[OLLAMA RAW]:", data)
        return data.get("response", "").strip().lower()
    except Exception as e:
        print("LLM error:", e)
        return "unknown"

def detect_intent(message):
    prompt = f"""
You are an assistant for a calendar booking app. Classify the user's intent as one of:
- book
- check
- list
- unknown

Message: "{message}"
Intent (only one word):
"""
    response = call_llm(prompt)
    allowed = ["book", "check", "list", "unknown"]
    return response if response in allowed else "unknown"

def parse_message(msg):
    try:
        dt = parser.parse(msg, fuzzy=True)
        start_time = dt
        end_time = start_time + timedelta(hours=1)
        return start_time, end_time
    except:
        return None, None

def langgraph_response(message):
    intent = detect_intent(message)
    print("[INTENT DETECTED]:", intent)

    if intent == "list":
        events = get_upcoming_events()
        if not events:
            return "🗓️ You have no upcoming events."
        response = "🗓️ Here are your upcoming bookings:\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            response += f"• {summary} at {start}\n"
        return response

    elif intent == "check":
        start, end = parse_message(message)
        if not start:
            return "❌ Sorry, I couldn’t understand the time you mentioned."

        if start.hour == 0 and start.minute == 0:
            events = get_events_on_day(start)
            if not events:
                return f"✅ You are free all day on {start.strftime('%A, %Y-%m-%d')}"
            response = f"❌ You have the following calls on {start.strftime('%A, %Y-%m-%d')}:\n"
            for e in events:
                summary = e.get('summary', 'No Title')
                time = e['start'].get('dateTime', e['start'].get('date'))
                response += f"• {summary} at {time}\n"
            return response
        else:
            if check_availability(start, end):
                return f"✅ You are free on {start.strftime('%A, %Y-%m-%d at %I:%M %p')}"
            else:
                return f"❌ You have a call on {start.strftime('%A, %Y-%m-%d at %I:%M %p')}"

    elif intent == "book":
        start, end = parse_message(message)
        if not start:
            return "❌ Sorry, I couldn’t understand the time you mentioned."

        if check_availability(start, end):
            result = create_event(start, end)
            if result.get("status") == "duplicate":
                return "⚠️ This event is already booked."
            return f"✅ Your call is booked for {start.strftime('%Y-%m-%d %I:%M %p')}"
        else:
            return "❌ That time slot is already booked. Try another?"

    else:
        return (
            "❌ Sorry, I couldn't understand your request. "
            "Try asking to book a call, check your availability, or list your bookings."
        )
