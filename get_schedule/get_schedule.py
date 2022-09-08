from __future__ import print_function
import googleapiclient
from httplib2 import Http
from oauth2client import file, client, tools
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdrivermanager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
import getpass
import time

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
    return [USERNAME, PASSWORD]

# def send_email(credentials): #send_email asks if the user wants an email sent to him/her with calendar info
#     global global_email
#     global bool_send_email
#     USERNAME = credentials[0]
#     email = USERNAME + "@bu.edu"
#     send_email = input('Would you like your calendar sent via email (Y/N)? \nMac users: the email will allow you to add this to your calendar app.\n ')
#     while send_email.lower() not in {'y','n'}:
#         send_email = input('You must enter yes(Y) or no(N) input not case sensitive: ')
#     if(send_email.lower() == 'y'):
#         print("Noted... An email will be sent to", email, "with more information.")
#         print("")
#         global_email = email
#         bool_send_email = True
#     else:
#         print("Noted...")
#         print("")
#         global_email = email
#         bool_send_email = False

def get_pelo_data(credentials): 
#logs into the bu website and pulls all your calendar data
    USERNAME = credentials[0]
    PASSWORD = credentials[1]
    changed_credentials = []
    return_list = []
    temp_url = ""
    is_logged_in = False
    line = "/html/body/table[3]/tbody/tr["
    prof_name = "]/td[5]/font/text()[2]"
    print("Logging in. Allow up to 30s due to exception handling.")
    #logging into the peloton website using a automated Google Chrome window
    # driver = webdriver.Chrome("/Users/miablo/Downloads/chromedriver")
    #location of automated Chrome exe file

    path = ("/Users/miablo/Downloads/chromedriver")
    s = Service(path)
    driver = webdriver.Chrome(service=s)

    # driver = webdriver.Chrome("/Users/miablo/Downloads/chromedriver")
    driver.set_page_load_timeout(30)
    driver.get("https://auth.onepeloton.com/login") #url
    driver.maximize_window()
    driver.implicitly_wait(20)
    driver.find_element("name", "usernameOrEmail").send_keys(USERNAME) #entering the username
    driver.find_element("name", "password").send_keys(PASSWORD) #entering the password
    temp_url = driver.current_url

    WebDriverWait(driver, TimeSpan.FromSeconds(20)).Until(ExpectedConditions.ElementToBeClickable(By.XPath("//button[@type/='submit']"))).Click();

    while is_logged_in == False:
        try:
            if (driver.find_element_by_xpath("//*[@id='wrapper']/div/h1").text == "Web Login"): #checking if the login was successful
                driver.quit()
                print("\nIncorrect username or password. Please try again.")
                changed_credentials = login("correct pelo")
                USERNAME = changed_credentials[0]
                PASSWORD = changed_credentials[1]
                print("Logging in. Allow up to 30s due to exception handling.")
                #logging into the BU website using a automated Google Chrome window
                driver = webdriver.Chrome(service=s)

                driver.set_page_load_timeout(30)
                driver.get("https://auth.onepeloton.com/login") #url
                driver.maximize_window()
                driver.implicitly_wait(20)
                driver.find_element_by_class_name("InputWithLabelView__Container-sc-1nfk2v2-0 eItdDS").send_keys(USERNAME) #entering the username
                driver.find_element_by_class_name("InputWithLabelView__Container-sc-1nfk2v2-0 eItdDS").send_keys(PASSWORD) #entering the password
                driver.find_element_by_class_name("buttons__Button1-sc-5819zz-0 buttons__Button1Large-sc-5819zz-1 SubmitButton__ActionButton-nki0x6-0 hlkwmh fHUuvL bDeiPM Form__StyledSubmitButton-sc-1silpjw-0 cKsDLr").click() #clicking the login button
        except NoSuchElementException:
            print("Login successful!\n")
            is_logged_in = True

    for i in range(2,15): #this loop iterates from the second tr class (inside the tbody class) to the 15th
        line = line + str(i) + "]" #line edits the xpath variable
        temp_var = driver.find_element_by_xpath(line) #this pulls the text from the 'line' xpath location
        return_list.append(temp_var.text) #each line is appended to the return_list
        line = "/html/body/table[3]/tbody/tr["
    driver.quit() #quitting the online session
    return return_list

def simplify(data): #simplifies the data that get_bu_data returns
    data[0] = data[0][40:] #removes the first 40 characters of the first string within data
    return_list = []
    line = ""
    for x in data:
        for y in x:
            if y != '\n': #removes endl's
                line = line+y
            if y == '\n': #replaces endl's with a space
                line = line + " "
        if(line[0:6] == "Summer"):
            return return_list
        if(line != "" and line[0:6] != "Summer"): #appends the edited data to return_list as long as its not empty or starting with 'Summer'
            return_list.append(line)
        line = ""
    return return_list

def parse(data): #takes the simplified data and turns it into a list of lists contianing strings [["",""],["",""]]
    omitted_variables = {"no","room","arranged"}
    line = ""
    temp1 = []
    temp2 = []
    temp3 = []
    temp4 = []
    temp5 = []
    for x in data:
        for y in x:
            if y != " ":
                line = line + y
            if y == " " and line != "" and line != "Class" and line != "Full":
                temp2.append(line)
                line = ""
        if "Class" in line or "Full" in line:
            line = ""
        if line != "":
            temp2.append(line)
            line = ""
        if temp2 != []:
            temp3.append(temp2)
            temp2 = []
    for a in temp3:
        for b in a:
            if b.lower() not in omitted_variables:
                temp4.append(b)
        temp5.append(temp4)
        temp4 = []
    return temp5

def new_cal_event(summary, location, start_datetime, end_datetime, recurrence): #adds an event to your calendar
    #print(summary,"||", location,"||", start_datetime,"||", end_datetime,"||", recurrence,"||", email)
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
        "recurrence": [
            recurrence,
        ],
        
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
    
def week_finder(week): 
#takes the given days of the week and turns them into dates 
    week_dict = {"Mon":23, "Tue":24, "Wed":25, "Thu":26, "Fri":27} 
    #days of the week with their cooresponding date on the first week of classes in spring 2017
    line = ""
    return_list = []
    try:
        for x in week:
            if x != ',':
                line = line + x
            if x == ',':
                return_list.append(week_dict[line])
                line = ""
        return_list.append(week_dict[line])
        return return_list
    except KeyError:
        return []

def start_to_militarty_time(i): 
#takes the start time that has been webscraped and turns it into military time
    start_datetime = ""
    if "".join(i[-2][-2:]) == "pm":
        if int("".join(i[-2][:-5])) != 12:
            start_datetime = str(int(i[-2][:-5]) + 12) + i[-2][-5:-2]
        if int("".join(i[-2][:-5])) == 12:
            start_datetime = i[-2][:-2]
    if "".join(i[-2][-2:]) == "am":
        start_datetime = i[-2][:-2]
    return str(start_datetime)

def end_to_military_time(i): 
#takes the end time that has been webscraped and turns it into military time
    end_datetime = ""
    if "".join(i[-1][-2:]) == "pm":
        if int("".join(i[-1][:-5])) != 12:
            end_datetime = str(int(i[-1][:-5]) + 12) + i[-1][-5:-2]
        if int("".join(i[-1][:-5])) == 12:
            end_datetime = i[-1][:-2]
    if "".join(i[-1][-2:]) == "am":
        end_datetime = i[-1][:-2]
    return str(end_datetime)

#executing the functions
credentials = login("Peloton") #getting username and password
# send_email(credentials)#checking if user wants an email
data = get_pelo_data(credentials) #scraping the website
data = simplify(data) #simplifying data
data = parse(data) #making data usable
print(data)

#declaring the variables needed to call new_cal_event
EVENT = {}
start_time_of_day = ""
end_time_of_day = ""
length = 0
summary = ""
location = ""
start_datetime = ""
end_datetime = ""
recurrence = "RRULE:FREQ=WEEKLY;UNTIL=20170428T170000Z"
days_of_week = []

#start of google API code
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
SCOPES = 'https://www.googleapis.com/auth/calendar'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store, flags) \
            if flags else tools.run(flow, store)
CAL = build('calendar', 'v3', http=creds.authorize(Http()))

#using the simplified and parsed data to add new calendar events
for i in data:
    length = len(i)
    summary = " ".join(i[5:-7])
    summary = summary + " " + str(i[-6]) + "-" + str(i[-7])
    location = str(i[-5]) + str(i[-4])
    start_time_of_day = start_to_militarty_time(i)
    end_time_of_day = end_to_military_time(i)
    days_of_week = week_finder(i[-3])

#becuase classes can be more than one day of the week the loop makes sure each day of the week is added
    if days_of_week != []:
        for j in days_of_week:
            start_datetime = "2017-01-"+ str(j) +"T" + start_time_of_day + ":00.000"
            end_datetime = "2017-01-"+ str(j) + "T" + end_time_of_day +":00.000"
            #adding the event to your google calendar
            new_cal_event(summary, location, start_datetime, end_datetime, recurrence)
print("\nYour scheudle has been updated. Check your email/google calendar.\n")
