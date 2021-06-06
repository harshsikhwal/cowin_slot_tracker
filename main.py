import requests
import datetime
import beepy
import threading
import time
import sys
import json

BASE_URL = r"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode="
PINCODE = "734001"
CENTER_NAME = r"suraksha"
cancel_val = "v"

def parse_response_json(vac_json):
    centers = vac_json['centers']
    available_center = {}
    available_center[CENTER_NAME] = "False"
    available_center["slots count"] = "0"
    available_sessions = []
    for center in centers:
        if CENTER_NAME in center['name'].lower():
            sessions = center['sessions']
            for session in sessions:
                available_session = {}
                if session['available_capacity_dose1'] > 0:
                    available_session['session_id'] = session['session_id']
                    available_session['date'] = session['date']
                    available_session['min_age_limit'] = session['min_age_limit']
                    available_session['available_capacity_dose1'] = session['available_capacity_dose1']
                    available_sessions.append(available_session)
            available_center[CENTER_NAME] = center['name']
    if len(available_sessions) != 0:
        available_center['slots count'] = len(available_sessions)
        available_center['slots'] = available_sessions
    return available_center

def alarm():
    global cancel_val
    while True:
        beepy.beep(sound=6)
        if cancel_val == 'c':
            cancel_val = 'v'
            break
    return

def raise_error_alarm():
    # raise alarm for 1 minute
    for i in range(0, 30):
        beepy.beep(sound=1)
        time.sleep(2)
    return

def raise_alarm():
    global cancel_val
    t1 = threading.Thread(target=alarm)
    t1.start()
    cancel_val = input("Press c to cancel alarm: ")
    t1.join()


def process_response(avail_json):
    center = avail_json[CENTER_NAME]
    slot_count = avail_json["slots count"]
    if center == "False":
        print(CENTER_NAME, " not available")
        return
    else:
        print(center, " available")
        if str(slot_count) == '0':
            print("Slots unavailable")
            print("Retrying")
            return
        else:
            print("Slots available")
            slots = avail_json["slots"]
            for slot in slots:
                t = time.localtime()
                current_time = time.strftime("%H:%M:%S", t)
                strdate = datetime.date.today()
                date = str(strdate.day) + "-" + str(strdate.month) + "-" + str(strdate.year)
                print("Current Date Current Time\t\t\tDate\t\tAge Limit\t\tAvailable Capacity Dose")
                print(date, "     ", current_time, "\t\t", slot["date"], "\t\t", str(slot["min_age_limit"]), "\t\t", str(slot["available_capacity_dose1"]))
            raise_alarm()


def fetch_data():
    strdate = datetime.date.today()
    date = str(strdate.day) + "-" + str(strdate.month) + "-" + str(strdate.year)
    Request_URL = BASE_URL + PINCODE + "&date=" + date
    print("Request: ", Request_URL)
    resp = requests.get(Request_URL)
    print("Response: ", resp.status_code, " Reason: ", resp.reason)
    if resp.status_code != 200:
        raise_error_alarm()
        print(resp.json())
        return -1
    available_centers = parse_response_json(resp.json())
    process_response(available_centers)
    return 1


def runner():
    strdate = datetime.date.today()
    date = str(strdate.day) + "-" + str(strdate.month) + "-" + str(strdate.year)
    print("The script will check whether First Dose Vaccines are available in Suraksha in cowin for pincode 734001 every 30 seconds for date: ", date)
    while True:
        if fetch_data() == -1:
            print("Error raised in last request. Check the response json")
            return
        try:
            for i in range(30, 0, -1):
                msg = f"No viable options. Next update in {i} seconds."
                print(msg, end="\r", flush=True)
                sys.stdout.flush()
                time.sleep(1)
        except KeyboardInterrupt:
            print()
            print("Exiting", end="\r", flush=True)
            return


def test_code():
    f = open('test.json')
    data = json.load(f)
    available_centers = parse_response_json(data)
    process_response(available_centers)


def main():
    # raise_alarm()
    runner()
    # test_code()

if __name__ == "__main__":
    main()

