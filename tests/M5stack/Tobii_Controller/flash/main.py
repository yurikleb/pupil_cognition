# A smaple code to control the Tobii-Glasses pro Eye Tracker
# Creates a new Project on the tracker.

from m5stack import lcd
import time

# microPython of "urllib.request" version is "urequests"
# https://github.com/micropython/micropython-lib/blob/master/urequests/urequests.py
import urequests


GLASSES_IP = "192.168.71.50"  # IPv4 address
PORT = 49152
base_url = 'http://' + GLASSES_IP
timeout = 1
api_action = '/api/projects'

url = base_url + api_action
data = None


# lcd.clear()
# lcd.setCursor(0, 0)
# lcd.setColor(lcd.WHITE)

time.sleep_ms(500)

lcd.print('Creating new Project...\n')

res = urequests.request("POST", url, headers={"Content-Type": "application/json"})

print(res.content)
lcd.print("PROJECT DATA: {} \n".format(res.content))



