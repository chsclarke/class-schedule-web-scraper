from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdrivermanager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from selenium.webdriver.common.by import By

import getpass

import time
import datetime as DateTime
from datetime import date

"""
Created on Tue Apr 25 18:45:37 2017
Copyright 2017 Chase Clarke cfclarke@bu.edu

"""

"""

Modified Wed Sep 7 08:45PM 2022
By: Mio Diaz

"""

def login(loginInfo): #this is the login function
    #loginInfo is a string of what you are logging into
    #userinput of username and password in a secure format
    global username_password

    print("#--------------------------------------------#")
    print("Enter your",loginInfo,"login information: ")
    USERNAME = input('Username: ')
    PASSWORD = getpass.getpass('Password:') #getpass makes it more secure as noone can see it being typed
    print("#--------------------------------------------#")
    print("")
    username_password = [USERNAME, PASSWORD]

    if len(username_password) != 0:
        print("Password and username stored successfully")

    return [USERNAME, PASSWORD]

def get_pelo_data(credentials): 
#logs into the bu website and pulls all your calendar data
    USERNAME = credentials[0]
    PASSWORD = credentials[1]
    changed_credentials = []
    return_list = []
    temp_url = ""
    login_url = "https://auth.onepeloton.com/login"
    successful_login_url ="https://members.onepeloton.com/schedule/cycling"
    is_logged_in = False

    print("Logging in. Allow up to 30s due to exception handling.")
    #logging into the peloton website using a automated Google Chrome window
   
    #location of automated Chrome exe file
    path = ("/Users/miablo/Downloads/chromedriver")
    s = Service(path)
    driver = webdriver.Chrome(service=s)

    driver.set_page_load_timeout(30)
    driver.get(login_url) #url
    driver.maximize_window()

    driver.implicitly_wait(10)

    driver.find_element("name", "usernameOrEmail").send_keys(USERNAME) #entering the username
    driver.find_element("name", "password").send_keys(PASSWORD) #entering the password

    WebDriverWait(driver, 10).until(ExpectedConditions.element_to_be_clickable((By.XPATH, "//div[@id='__next']/section/div/div/form/button"))).click()

    time.sleep(5)

    temp_url = driver.current_url

    while is_logged_in == False:
        try:

            time.sleep(5)

            print(login_url)
            print(temp_url)

            if (login_url in temp_url): #checking if the login was successful
                driver.quit()

                print("\nIncorrect username or password. Please try again.")
                changed_credentials = login("correct pelo")
                USERNAME = changed_credentials[0]
                PASSWORD = changed_credentials[1]
                print("Logging in. Allow up to 30s due to exception handling.")

                driver = webdriver.Chrome(service=s)

                driver.set_page_load_timeout(30)
                driver.get(login_url) #url
                # driver.maximize_window()

                driver.implicitly_wait(20)
                driver.find_element("name", "usernameOrEmail").send_keys(USERNAME) #entering the username
                driver.find_element("name", "password").send_keys(PASSWORD) #entering the password

                WebDriverWait(driver, 10).until(ExpectedConditions.element_to_be_clickable((By.XPATH, "//div[@id='__next']/section/div/div/form/button"))).click() #clicking the login button


                time.sleep(5)

                temp_url = driver.current_url

            else:
                print("Login successful!\n")
                is_logged_in = True

        except NoSuchElementException:
            print("Login successful!\n")
            is_logged_in = True

    WebDriverWait(driver, 5).until(ExpectedConditions.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/schedule')]"))).click()

    WebDriverWait(driver, 7).until(ExpectedConditions.element_to_be_clickable((By.XPATH, "//div[@id='categories']/nav/div/div/a[2]"))).click()

    # # find all the dates and store that data for use later
    # date_time = DateTime.datetime.now()
    # # make time substring - remove 24hr portion of current time
    # unix_timestamp_substring = str(time.mktime(date_time.timetuple()))[:5]
    # # add in the 4 pm timestamp to the first 5 numbers in the timestamp 
    # # to create a timestamp with the current day but time of 4 pm
    element_id_timestamp = str(get_unix_time())

    print(element_id_timestamp)

    driver.find_element("name", "week-0")
    # loop through week-0 div and get dates
    for i in range(0,7): 
        # alway calculate day that starts at 4 GMT
        temp_var =  driver.find_element("name", element_id_timestamp) 
        return_list.append(temp_var.text) #each line is appended to the return_list
        element_id_timestamp = str(int(element_id_timestamp) + 86400)

    driver.find_element("name", "week-1")
    # loop through week-1 div and get dates
    for i in range(0,7): 
        # alway calculate day that starts at 4 GMT
        temp_var =  driver.find_element("name", element_id_timestamp) 
        return_list.append(temp_var.text) #each line is appended to the return_list
        element_id_timestamp = str(int(element_id_timestamp) + 86400)
        
    driver.quit() #quitting the online session
    return return_list


def get_unix_time():
 # find all the dates and store that data for use later
    date_time = date.today()

    unix_time = DateTime.datetime(date_time.year, date_time.month, date_time.day, 00, 00)

    # make time substring - remove 24hr portion of current time
    element_id_timestamp = str(time.mktime(unix_time.timetuple()))[:10]
    # add in the 4 pm timestamp to the first 5 numbers in the timestamp 
    # to create a timestamp with the current day but time of 4 pm
    # element_id_timestamp = unix_timestamp_substring + "09600"

    # print(date_time)
    # print(unix_time)
    # print(element_id_timestamp)

    return element_id_timestamp

    # 1662696000
    # 1662709600

    # Example output data
    # ['THURSDAY, SEPTEMBER 8\n7:00 PM\nLIVE\n20 min Tabata Ride\nKENDALL TOOLE · CYCLING', 'FRIDAY, SEPTEMBER 9\nNo Classes', 'SATURDAY, SEPTEMBER 10\nNo Classes', 'SUNDAY, SEPTEMBER 11\nNo Classes', 'MONDAY, SEPTEMBER 12\nNo Classes', 'TUESDAY, SEPTEMBER 13\nNo Classes', 'WEDNESDAY, SEPTEMBER 14\n12:35 PM\nLIVE\n20 min Low Impact Ride\nROBIN ARZÓN · CYCLING\nYOU’RE IN', 'THURSDAY, SEPTEMBER 15\n7:00 PM\nLIVE\n30 min 90s Pop Ride\nKENDALL TOOLE · CYCLING\nYOU’RE IN', 'FRIDAY, SEPTEMBER 16\n5:30 PM\nLIVE\n30 min Latin Ride\nROBIN ARZÓN · CYCLING\nYOU’RE IN', 'SATURDAY, SEPTEMBER 17\nNo Classes', 'SUNDAY, SEPTEMBER 18\nNo Classes', 'MONDAY, SEPTEMBER 19\nNo Classes', 'TUESDAY, SEPTEMBER 20\nNo Classes', 'WEDNESDAY, SEPTEMBER 21\nNo Classes']

def simplify(data): #simplifies the data that get_pelo_data returns
    data[0] = data[0] 

    return_list = []
    line = ""

    for x in data:
        for y in x:
            if y != '\n': #removes endl's
                line = line+y
            if y == '\n': #replaces endl's with a space
                line = line + " "
        # if(line[0:7] == "No Classes"):
        #     return return_list
        # if(line != "" and line[0:7] != "No Classes"): #appends the edited data to return_list as long as its not empty or starting with 'Summer'
        #     return_list.append(line)
        line = ""
    return return_list

# def start_to_militarty_time(i): 
# #takes the start time that has been webscraped and turns it into military time
#     start_datetime = ""
#     if "".join(i[-2][-2:]) == "pm":
#         if int("".join(i[-2][:-5])) != 12:
#             start_datetime = str(int(i[-2][:-5]) + 12) + i[-2][-5:-2]
#         if int("".join(i[-2][:-5])) == 12:
#             start_datetime = i[-2][:-2]
#     if "".join(i[-2][-2:]) == "am":
#         start_datetime = i[-2][:-2]
#     return str(start_datetime)

# def end_to_military_time(i): 
# #takes the end time that has been webscraped and turns it into military time
#     end_datetime = ""
#     if "".join(i[-1][-2:]) == "pm":
#         if int("".join(i[-1][:-5])) != 12:
#             end_datetime = str(int(i[-1][:-5]) + 12) + i[-1][-5:-2]
#         if int("".join(i[-1][:-5])) == 12:
#             end_datetime = i[-1][:-2]
#     if "".join(i[-1][-2:]) == "am":
#         end_datetime = i[-1][:-2]
#     return str(end_datetime)

#executing the functions
credentials = login("Peloton") #getting username and password

data = get_pelo_data(credentials) #scraping the website
print(data)
data = simplify(data) #simplifying data
print(data)
calendar_api_call()


#declaring the variables needed to call new_cal_event
event = {}

start_time_of_day = ""
end_time_of_day = ""

length = 0

summary = ""

start_datetime = ""
end_datetime = ""

days_of_week = ""


### TODO
## Research google api
## determine how build event for calendar event
## create function to pull duration of class and time of class to create end_time var
## determine what part will go into the event name ++ summary 
###

## https://developers.google.com/calendar/api/v3/reference
def new_cal_event(): 
    # Build event response body for calendar event for each class in schedule
    event = {
      'summary': 'Google I/O 2015',
      'location': '800 Howard St., San Francisco, CA 94103',
      'description': 'A chance to hear more about Google\'s developer products.',
      'start': {
        'dateTime': '2015-05-28T09:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
      },
      'end': {
        'dateTime': '2015-05-28T17:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
      },
      'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=2'
      ],
      'attendees': [
        {'email': 'lpage@example.com'},
        {'email': 'sbrin@example.com'},
      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()

#start of google API code
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def calendar_api_call():
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')

        # events_result = service.events().list(calendarId='primary', timeMin=now,
        #                                       maxResults=10, singleEvents=True,
        #                                       orderBy='startTime').execute()
        # events = events_result.get('items', [])

        # if not events:
        #     print('No upcoming events found.')
        #     return

        # # Prints the start and name of the next 10 events
        # for event in events:
        #     start = event['start'].get('dateTime', event['start'].get('date'))
        #     print(start, event['summary'])

    except HttpError as error:
        print('An error occurred: %s' % error)

print("\nYour schedule has been updated. Check your google calendar.\n")
