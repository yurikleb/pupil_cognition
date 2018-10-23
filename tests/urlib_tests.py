import urllib.request
import json


GLASSES_IP = "192.168.71.50"  # IPv4 address
PORT = 49152
base_url = 'http://' + GLASSES_IP
timeout = 1
api_action = '/api/projects'


url = base_url + api_action

req = urllib.request.Request(url)
data = None
req.add_header('Content-Type', 'application/json')

data = json.dumps(data)
response = urllib.request.urlopen(req, data.encode())
data = response.read()
json_data = json.loads(data)

print(json_data['pr_id'])


# Micropython Version:
# import urequests
# res = urequests.request("POST", url, headers={"Content-Type": "application/json"})


# {"wifi": {"ssid": "designlab-ws-dell", "password": "123gsuffa"}}