import time
import requests

URL = "https://chiwegames.com"

def ping_site():
    try:
        response = requests.get(URL, timeout=10)
        if response.status_code == 200:
            print(f"[OK] Site is up. Status: {response.status_code}")
        else:
            print(f"[WARN] Site responded with status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not reach site: {e}")

if __name__ == "__main__":
    while True:
        ping_site()
        time.sleep(180)  #wait 3 minutes 
