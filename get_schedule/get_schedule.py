from __future__ import print_function
import googleapiclient
from httplib2 import Http
from oauth2client import file, client, tools
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

    # find all the dates and store that data for use later
    date_time = DateTime.datetime.now()
    # make time substring - remove 24hr portion of current time
    unix_timestamp_substring = str(time.mktime(date_time.timetuple()))[:5]
    # add in the 4 pm timestamp to the first 5 numbers in the timestamp 
    # to create a timestamp with the current day but time of 4 pm
    element_id_timestamp = unix_timestamp_substring + "09600"

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
        if(line[0:7] == "No Classes"):
            return return_list
        if(line != "" and line[0:7] != "No Classes"): #appends the edited data to return_list as long as its not empty or starting with 'Summer'
            return_list.append(line)
        line = ""
    return return_list

def new_cal_event(summary, location, start_datetime, end_datetime): #adds an event to your calendar
    print(summary,"||", location,"||", start_datetime,"||", end_datetime,"||", email)
    EVENT = {
        "summary": summary,
        "location": location,
        "start": {
            "dateTime": start_datetime,
            "timeZone": "America/New_York"
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": "America/New_York"
        },
        "attendees": [
            {
                "email": global_email,
            },
            # ...
        ],
    }
    e = CAL.events().insert(calendarId='primary', sendNotifications=bool_send_email, body=EVENT).execute()
    print('''*** %r event added:
        Start: %s
        End:   %s''' % (e['summary'].encode('utf-8'), e['start']['dateTime'], e['end']['dateTime']))

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
# send_email(credentials)#checking if user wants an email
data = get_pelo_data(credentials) #scraping the website
print(data)
data = simplify(data) #simplifying data
# data = parse(data) #making data usable
print(data)

#declaring the variables needed to call new_cal_event
EVENT = {}

start_time_of_day = ""
end_time_of_day = ""

length = 0

summary = ""

start_datetime = ""
end_datetime = ""

days_of_week = ""

#start of google API code
# try:
#     import argparse
#     flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
# except ImportError:
#     flags = None
# SCOPES = 'https://www.googleapis.com/auth/calendar'
# store = file.Storage('storage.json')
# creds = store.get()
# if not creds or creds.invalid:
#     flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
#     creds = tools.run_flow(flow, store, flags) \
#             if flags else tools.run(flow, store)
# CAL = build('calendar', 'v3', http=creds.authorize(Http()))

#using the simplified and parsed data to add new calendar events
# for i in data:
#     length = len(i)
#     summary = " ".join(i[5:-7])
#     summary = summary + " " + str(i[-6]) + "-" + str(i[-7])
#     start_time_of_day = start_to_militarty_time(i)
#     end_time_of_day = end_to_military_time(i)
#     days_of_week = i[0]

print("\nYour schedule has been updated. Check your google calendar.\n")
