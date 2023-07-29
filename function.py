import datefinder
from api_call import service
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError
from api_call import service
import datefinder
import pytz
from dotenv import load_dotenv

load_dotenv()

# Function to get upcoming events with their IDs
def get_upcoming_events(service):
    try:
        now = datetime.utcnow().isoformat() + "Z"
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return None

        return events

    except HttpError as error:
        print("An error occurred: %s" % error)
        return None


def list_upcoming_events():
    events = get_upcoming_events(service)
    if events:
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"], event["id"])


def delete_event(event_name):
    events = get_upcoming_events(service)
    if events:
        matching_events = [event for event in events if event["summary"].lower() == event_name.lower()]
        if matching_events:
            print("Matching events to be deleted:")
            for event in matching_events:
                print(event["start"].get("dateTime", event["start"].get("date")), event["summary"], event["id"])

            confirmation = input("Do you want to delete these events? (yes/no): ")
            if confirmation.lower() == "yes":
                for event in matching_events:
                    event_id = event["id"]
                    try:
                        service.events().delete(calendarId="primary", eventId=event_id).execute()
                        print("Event deleted successfully:", event["summary"])
                    except HttpError as e:
                        print(f"An error occurred while deleting the event: {e}")
            else:
                print("Event deletion cancelled.")
        else:
            print("No matching events found.")
    else:
        print("No upcoming events found.")


def create_event(date, time, name, duration=1, description=None, location=None):
    
    start_time_str = date + " " +time
    matches = list(datefinder.find_dates(start_time_str))
    if len(matches):
        start_time = matches[0]
        end_time = start_time + timedelta(hours=duration)

        event = {
            'summary': name,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'Asia/Kolkata',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        try:
            event_result = service.events().insert(calendarId="primary", body=event).execute()
            print("Event created successfully!")
            return event_result
        except HttpError as e:
            print(f"An error occurred while creating the event: {e}")
            return None
    else:
        print("Error: Invalid format. Event not created.")
        return None

import datefinder
from googleapiclient.errors import HttpError

def update_event(event_name, **kwargs):
    events = get_upcoming_events(service)
    if events:
        matching_events = [event for event in events if event["summary"].lower() == event_name.lower()]
        if matching_events:
            print("Matching events to be updated:")
            for event in matching_events:
                print(event["start"].get("dateTime", event["start"].get("date")), event["summary"], event["id"])
            print(event["start"].get("dateTime"))
            print(event["end"].get("dateTime"))
            confirmation = input("Do you want to update these events? (yes/no): ")
            if confirmation.lower() == "yes":
                for event in matching_events:
                    event_id = event["id"]
                    try:
                        updated_event = service.events().get(calendarId="primary", eventId=event_id).execute()
                        print(event["start"].get("duration"))
                        date = kwargs.get("date")
                        start_hours, start_minutes = map(int, [event["start"]["dateTime"][11:13], event["start"]["dateTime"][14:16]])
                        end_hours, end_minutes = map(int, [event["end"]["dateTime"][11:13], event["end"]["dateTime"][14:16]])

                        # Calculate the time difference using timedelta
                        duration = kwargs.get("duration")
                        if duration:
                            time_difference = timedelta(hours=duration)
                        else :
                            time_difference = timedelta(hours=end_hours - start_hours, minutes=end_minutes - start_minutes)
                            
                        if date:
                            start_time_str = date + " " + updated_event["start"].get("dateTime")[11:16]  # Extracting time from dateTime
                            matches = list(datefinder.find_dates(start_time_str))
                            if len(matches):
                                start_time = matches[0]
                                end_time = start_time + time_difference
                                updated_event['start']['dateTime'] = start_time.strftime("%Y-%m-%dT%H:%M:%S")
                                updated_event['end']['dateTime'] = end_time.strftime("%Y-%m-%dT%H:%M:%S")

                        time = kwargs.get("time")
                        if time:
                            start_time_str = updated_event["start"].get("dateTime")[:10] + " " + time  # Extracting date from dateTime
                            matches = list(datefinder.find_dates(start_time_str))

                            if len(matches):
                                start_time = matches[0]
                                updated_event['start']['dateTime'] = start_time.strftime("%Y-%m-%dT%H:%M:%S")
                                if len(matches):
                                    start_time = matches[0]
                                    end_time = start_time +time_difference
                                    updated_event['start']['dateTime'] = start_time.strftime("%Y-%m-%dT%H:%M:%S")
                                    updated_event['end']['dateTime'] = end_time.strftime("%Y-%m-%dT%H:%M:%S")
                        print("Start time : " + start_time_str)
                        
                        name = kwargs.get("name")
                        if name:
                            updated_event['summary'] = name

                        description = kwargs.get("description")
                        if description:
                            updated_event['description'] = description

                        location = kwargs.get("location")
                        if location:
                            updated_event['location'] = location

                        updated_event = service.events().update(calendarId="primary", eventId=event_id, body=updated_event).execute()
                        print("Event Updated Successfully:", updated_event["summary"])

                    except HttpError as e:
                        print(f"An error occurred while updating the event: {e}")
            else:
                print("Event update cancelled.")
        else:
            print("No matching events found.")
    else:
        print("No upcoming events found.")

# to send message to WhatsApp
from twilio.rest import Client
import os

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

def send_message(to: str, message: str) -> None:
    '''
    Send message to a Telegram user.

    Parameters:
        - to(str): sender whatsapp number in this whatsapp:+919558515995 form
        - message(str): text message to send

    Returns:
        - None
    '''

    _ = client.messages.create(
        from_=os.getenv('FROM'),
        body=message,
        to=to
    )
