import gspread as gs
import requests
import json
import random as rd
from time import sleep
import datetime
from datetime import timedelta
import subprocess
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-x', action='store_true')
args = parser.parse_args()

if args.x:
    print("Cross posting enabled")

creds = {} # REDACTED

gc = gs.service_account_from_dict(creds)
sh = gc.open("V.A Reddit's strategy sheet V.A RVL")

with open("jeton.txt", "r") as f:
    TOKEN = f.readlines()[0]

REDDIT = "https://www.reddit.com"

profiles_test = ... # REDACTED
ids_test = ... # REDACTED


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

def rdp(L = [-3,-1,1,3]):
    return(rd.choice(L))

def getGologinProfiles():
    profiles_req = requests.get(url='https://api.gologin.com/browser/v2', headers= {'Authorization': f'Bearer {TOKEN}' , 
                                                                                     'Content-Type': 'application/json'})
    profiles = {}
    for k in json.loads(profiles_req.text)['profiles']:
        if k['name'].startswith("Reddit Sub"):
            profiles[k['name']] = k['id']
    return(profiles)

def retrieveSheetData():
    N_tabs = 50
    outp = {}
    W = sh.worksheet("Schedule posting")
    L = W.get(f'C2:C50')
    M=[]
    
    for k in L:
        if len(k)>0:
            try:
                M.append(int(k[0].split(" ")[-1]))
            except ValueError:
                continue
            
    n_subs = max(M)
    
    logins = sh.worksheet("Models accounts").get(f'B2:E50')
    loginsd={}
    for k in logins:
        if len(k) > 0 and len(k[0]) > 0:
            loginsd[k[3]] = k[0]
    
    for tab in range(N_tabs):
        d = {}
        L = W.get(f'A{tab*(n_subs+2)+1}:G{tab*(n_subs+2)+n_subs+1}')
        
        if len(L)>0:
            modelname = L[1][0]
            try:
                modelaccount = loginsd[L[1][0]]
            except KeyError:
                continue
            
            for bot in range(1,n_subs+1):
                d[L[bot][2]] = [L[bot][3], (L[bot][6])]
                
            outp[f"{modelname};{modelaccount}"] = d
    
    return(outp)

def transformSheetData(d: dict):
    outp = {k:[] for k in d[ list(d.keys())[0] ].keys()}
    for k in d.keys():
        modelname, modelaccount = k.split(";")
        for bot in outp.keys():
            outp[bot].append([modelaccount]+d[k][bot])
    return(outp)

def getBotLogins():
    data = sh.worksheet("Subs accounts").get(f'B2:D40')
    ids_={}
    for k in data:
        idd = k[2].replace("sub", "Sub")
        ids_[idd] = [k[0], k[1]]
    return(ids_)

def get_time_until_target(target_hour):
    Now = datetime.datetime.now()
    target_time = datetime.datetime(Now.year, Now.month, Now.day, target_hour, 0, 0)
    
    time_difference = target_time - Now
    return time_difference.total_seconds()+5

if __name__ == "__main__":
    # d = retrieveSheetData()
    # posts = transformSheetData(d)
    profiles = getGologinProfiles()
    ids_ = getBotLogins()
    
    if args.x:
        with open("comms.txt", "w", encoding="utf-8") as c:
            L = sh.worksheet("Comments to use with subs account").get('C2:C1000')
            L = [l[0]+"\n" for l in L]
            c.writelines(L)

    ##### Test variables #####
    # profiles = profiles_test
    # ids_ = ids_test
    # early = { ... }
    # late = early.copy()
    ##### Test variables #####
    
    print("\n\n- profiles:",profiles, end="\n")
    profiles.pop("Reddit Sub 14")
    print("\n\n- ids_:",ids_, end="\n")
    # print("\n\n- posts:",posts, end="\n")
    
    # with open("posts.json", "w") as f:
    #     f.write(json.dumps(posts))

    while True:
        Now = datetime.datetime.now()
        
        if Now.minute <= 60:
            print("Now is",Now,"; Beginning posting")
        else:
            print("Sleeping...")
            sleep(60)
            continue
        
        """timestamp_early = get_time_until_target(early_time) # 7 AM CET = 13:00 GMT+1
        closer_time = min(timestamp_early, timestamp_late)
        
        print(f"Waiting until {Now + timedelta(seconds=closer_time)}")
        print("To start the script now, hit Ctrl+C")

        try:
            sleep(closer_time)
        except KeyboardInterrupt:
            pass"""
                    
        for bot in profiles.keys():
            # print("Sleeping about 30s")
            # sleep(30 + rd.choice([-3,-5,0,5,3])) # Wait 60s to start new bot
            
            command = " ".join([
                        ".\\comments\\Scripts\\python.exe",
                            ".\\sender.py",
                            "--botname", "\""+ bot + "\" "
                            "--botid", str(profiles[bot]),
                            "--uname", ids_[bot][0], 
                            "--pwd", ids_[bot][1],
                            ("-x" if args.x else "")
                        ])
            
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()

            print("stdout:\n",stdout)
            print("\n\nstderr:\n",stderr)
            rc = process.returncode
            
            # if "404" in stderr:
            #     print("Model account not found")
            
            if "407" in stderr:
                print("Proxy issue (407)")
            elif "KeyError" in stderr:
                print("Bot not in Schedule posting sheet")
            elif "Host unreachable" in stderr:
                print("Proxy expired or unavailable")
            elif "not connected to DevTools" in stderr or "element click intercepted" in stderr:
                print("Window error")
            elif rc == 1:
                print("Another error occurred")
                # exit(1)
            