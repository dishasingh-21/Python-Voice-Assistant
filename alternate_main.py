from __future__ import print_function
import datetime
import pickle
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import time
import pyttsx3
import speech_recognition as sr
import pytz            #helps to get the current UTC time.

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENSIONS = ["nd", "rd", "st", "th"]

def speak(text):
    engine = pyttsx3.init()  #To get pytts get started. We need to do this everytime before we speak something.
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        said = ""
        try:
            audio = r.listen(source)
            print("Audio captured successfully!")
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print(f"Error capturing audio: {e}")
        
    return said

def authenticate_google():
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  service = build("calendar", "v3", credentials=creds)
    
  return service

def get_events(day, service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    ''' these varibales specify the starting and ending time, so that it only tells us the events which occur within this duration. '''

    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)
    events_result = (service.events().list(calendarId="primary", timeMin=date.isoformat(), timeMax = end_date.isoformat(), singleEvents=True, orderBy="startTime",).execute())
    events = events_result.get("items", [])

    if not events:
      speak("No upcoming events found.")
      return
    else:
        speak(f"You have {len(events)} on this day.")
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
            start_time = str(start.split("T")[1].split("+")[0].split(":")[0])
            if int(start_time) < 12:
               start_time = start_time + "am"
            else:
               start_time = str(int(start_time) - 12) + "pm"

            speak(event["summary"] + " at " + start_time)

def get_date(text):
   text = text.lower()
   today = datetime.date.today()
   
   if text.count("today") > 0:
      return today
   
   day = -1
   day_of_week = -1
   month = -1
   year = today.year
 
   for word in text.split():
      if word in MONTHS:
         month = MONTHS.index(word) + 1
      elif word in DAYS:
         day = DAYS.index(word) + 1
      elif word.isdigit():
         day = int(word)
      else:
         for ext in DAY_EXTENSIONS:
            found  = word.find(ext)
            if found > 0:
               try:
                  day = int(word[:found])
               except:
                  pass
    
   if month < today.month and month != -1:
      year = year + 1

   if day<today.day and month == -1 and day != -1:
      month = month + 1

   if day_of_week != -1 and month == -1 and day == -1:
      current_day = today.weekday()
      dif = day_of_week - current_day
      if dif < 0:
         dif += 7
         if word.count("next") >= 1:
            dif += 7

      return today + datetime.timedelta(dif)

   return datetime.date(month = month, day = day, year = year)

SERVICE = authenticate_google()
print("start")
text = get_audio()

CALENDER_STRS = ["am i busy", "do i have plans", "do i have something planned", "what's on my schedule", "anything"]
for phrase in CALENDER_STRS:
   if phrase in text.lower():
      date = get_date(text)
      if date:
        get_events(date, SERVICE)
      else:
        speak("I didn't understand. Please try again.")


'''Notes:
look at pytts gtts documentations.'''