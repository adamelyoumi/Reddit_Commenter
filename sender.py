
print("--------------------------------------------------------------------------------------------------\n--------------------------------------------------------------------------------------------------")

import praw
from prawcore.exceptions import NotFound as prawNotFound
import requests
from time import sleep
import json
import random as rd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, WebDriverException, NoAlertPresentException
from selenium.webdriver.common.alert import Alert
import gologin as g
from cwp import ChromeWithPrefs
import argparse
import re, os
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--botid', type=str)
parser.add_argument('--botname', type=str)
parser.add_argument('--uname', type=str)
parser.add_argument('--pwd', type=str)
# parser.add_argument('--t', type=str)
parser.add_argument('-x', action='store_true')
args = parser.parse_args()

print("Starting")

def remove_emojis(text):
    # Define the regular expression for detecting emojis
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F700-\U0001F77F"  # alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U00002702-\U000027B0"  # Dingbats
                               u"\U000024C2-\U0001F251" 
                               "]+", flags=re.UNICODE)

    # Remove emojis from the text
    cleaned_text = emoji_pattern.sub(r'', text)
    return cleaned_text

def count_substring(main_string, substring):
    count = 0
    start_index = 0

    while True:
        index = main_string.find(substring, start_index)
        if index == -1:
            break
        count += 1
        start_index = index + 1

    return count

def rdp(L = [-1,0,1]):
    return(rd.choice(L))

def login(browser, bot = [args.uname, args.pwd]):

    browser.get('https://old.reddit.com/login')

    sleep(2+rdp())
    browser.find_element(By.ID, 'user_login').click()
    browser.find_element(By.ID, 'user_login').send_keys(bot[0])

    sleep(2+rdp())

    browser.find_element(By.ID, 'passwd_login').click()
    browser.find_element(By.ID, 'passwd_login').send_keys(bot[1])
    sleep(2+rdp())

    browser.find_elements(By.CSS_SELECTOR, ".c-btn.c-btn-primary.c-pull-right")[1].click() # Sign in

def handle_alert(driver):
    try:
        driver.switch_to.alert.accept()
        print("Ignoring alert...")
    except NoAlertPresentException:
        pass
    return

try:
    with open("posts.json", "r") as f2:
        el_s = f2.readlines()[0]
        el = json.loads(el_s)

    bot = args.botname
    
    if args.x:
        coms = []
        for k in el.keys():
            coms += el[k]
        el = {bot: coms}
            
    chrome_driver_path = f"C:\\Users\\{os.getlogin()}\\.cache\\selenium\\chromedriver\\win32\\118.0.5993.70\\chromedriver-win64\\chromedriver.exe"
    chrome_service = Service(executable_path=chrome_driver_path)

    with open("jeton.txt", "r") as f:
        TOKEN = f.readlines()[0]

    REDDIT = "https://www.reddit.com"
    REDDIT_OLD = "https://old.reddit.com/"

    print(f"Starting profile with bot {bot}")
    gl = g.GoLogin({"token": TOKEN, 
                    "profile_id": args.botid, 
                    "executablePath": f"C:\\Users\\{os.getlogin()}\\.gologin\\browser\\orbita-browser-118\\chrome.exe"})

    debugger_address = gl.start()

    chrome_options = Options()

    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", {"credentials_enable_service": False, 
                                                    "profile.password_manager_enabled": False, 
                                                    "profile.default_content_setting_values.notifications": 2})

    chrome_options.add_experimental_option("debuggerAddress", debugger_address)
    chrome_options.add_argument("disable-notifications")

    api_username, api_password, api_client_id, api_client_secret = "No-Caterpillar7445","abcdefgh","LLYeM_fsC2eaOj8OH7Rbnw","kstHYpJHdrebwAZERtKTd4Ueh0Y82g"

    reddit = praw.Reddit(
        client_id=api_client_id,
        client_secret=api_client_secret,
        user_agent="test",
        username=api_username,
        password=api_password
    )

    driver = ChromeWithPrefs(service=chrome_service, options=chrome_options)

    driver.get(REDDIT_OLD)

    user = driver.find_elements(By.XPATH, '//span[@class="user"]')[0].text
    if re.match(args.uname, user) is None:
        print("Logging in")
        login(driver)
        sleep(1)
        driver.refresh()
        sleep(1)

    else:
        print("Already logged in")
        sleep(1)

    for comment in el[bot]:
        handle_alert(driver)
        
        acc, sub, txt = comment
        
        if args.x:
            with open("comms.txt", "r", encoding="utf-8") as c:
                commsList = c.readlines()
            
            commsList = [remove_emojis(s).replace("\n", "") for s in commsList]
            txt = rd.choice(commsList)
            
        sub = sub.removeprefix("r/")
        found = False
        print(f"Sending comment '{txt.encode()}' on {sub} in {acc} post.")
        u = reddit.redditor(acc)
        
        try:
            submissions = u.submissions.new(limit=50)
            _ = next(submissions)
            
        except prawNotFound:
            print(f"--> User {u} not found")
            continue
        
        submissions_L = list(submissions)
        submissions_Ls = reversed(sorted(submissions_L, key=lambda x: datetime.datetime.fromtimestamp(x.created)))
        
        for submission in submissions_Ls:
            if submission.subreddit.display_name == sub:
                try:
                    found = True
                    print(f"--> Found post by {acc} in subreddit {sub}. Title: {submission.title[:20]}...")
                    
                    driver.get(REDDIT + submission.permalink)
                    handle_alert(driver)
                    
                    sleep(10)
                    
                    if count_substring(driver.find_element(By.XPATH, '//div[@class="uI_hDmU5GSiudtABRz_37 "]').text, args.uname) > 1:
                        print("--> Already commented !")
                        break
                    
                    xButton = driver.find_elements(By.XPATH, '//button[@class="_3GEY4V1vCvw8HqDBo4DyQW"]')
                    if len(xButton) > 0:
                        x = xButton[0]
                        x.click()
                    
                    comBox = driver.find_elements(By.XPATH, '//div[@role="textbox"]')
                    if len(comBox) == 0:
                        print("--> Cannot comment, no comments box !")
                        break
                    
                    comBox = comBox[0]
                    comBox.click()
                    sleep(rdp([0.5,1]))
                    
                    comBox.send_keys(txt)
                    sleep(2 + rdp([0,1]))
                    
                    submitButton = driver.find_elements(By.XPATH, '//button[@class="_22S4OsoDdOqiM-hPTeOURa _2iuoyPiKHN3kfOoeIQalDT _10BQ7pjWbeYP63SAPNS8Ts _3uJP0daPEH2plzVEYyTdaH "]')[0]
                    
                    submitButton.click()
                    
                    print("--> Comment sent !")
                    sleep(3)
                    break
                except (ElementClickInterceptedException, WebDriverException) as e:
                    print("Error:", e)
                    print("Continuing on to the next comment...")
                    break
                    
        if not found:
            print("--> Post not found !")
        
except Exception as e:
    print("Error detected")
    requests.post("http://localhost:36912/browser/stop-profile", data={"profileId": args.botid})
    
    try:
        gl.stop()
        driver.close()
    except:
        pass
    raise e

print("Terminating...")
driver.close()

exit(0)