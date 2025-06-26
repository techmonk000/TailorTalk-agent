import os
import openai
from datetime import datetime, timedelta
from calender_utils import check_availability, create_event

openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_message(msg):
    
    if "tomorrow" in msg.lower():
        start_time = datetime.now() + timedelta(days=1)
        start_time = start_time.replace(hour=15, minute=0)
        end_time = start_time + timedelta(hours=1)
        return start_time, end_time
    return None, None

def langgraph_response(message):
    start, end = parse_message(message)
    if not start:
        return "Sorry, I didn’t understand the time you mentioned."

    if check_availability(start, end):
        create_event(start, end)
        return f"✅ Your call is booked for {start.strftime('%Y-%m-%d %I:%M %p')}"
    else:
        return "❌ That time slot is already booked. Try another?"
