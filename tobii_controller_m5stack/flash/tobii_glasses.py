# This Module sends commands to the Tobii Pro Glasses Eye Tracker
# Note:
# microPython of "urllib.request" version is "urequests"
# https://github.com/micropython/micropython-lib/blob/master/urequests/urequests.py


import urequests
import json
import time

GLASSES_IP = "192.168.71.50"  # IPv4 address
PORT = 49152
base_url = 'http://' + GLASSES_IP
timeout = 1


class TobiiRecording:
    def __init__(self):
        self.is_calibrated = False
        self.is_calibrating = False
        self.is_recording = False
        self.project_id = ''
        self.participant_id = ''
        self.calibration_id = ''
        self.recording_id = ''


def post_request(api_action, the_data=None):
    url = base_url + api_action
    the_data = json.dumps(the_data)
    response = urequests.request("POST", url, the_data.encode(), headers={"Content-Type": "application/json"})

    try:
        json_data = json.loads(response.content)
        return json_data
    except ValueError:
        return response.content

    # print(response.content)
    # lcd.print("RESPONSE: {} \n".format(response.content))


def wait_for_status(api_action, key, values):
    url = base_url + api_action
    running = True
    json_data = None

    while running:
        response = urequests.request("GET", url, headers={"Content-Type": "application/json"})
        json_data = json.loads(response.content)
        if json_data[key] in values:
            running = False
        time.sleep(1)

    return json_data[key]


def send_event(evtType, evtTag):
    data = {'ets': 0, 'type': evtType, 'tag': evtTag}
    response_data = post_request('/api/events', data)
    print(response_data)


def create_project():
    json_data = post_request('/api/projects')
    return json_data['pr_id']


def create_participant(project_id):
    data = {'pa_project': project_id}
    json_data = post_request('/api/participants', data)
    return json_data['pa_id']


def create_calibration(project_id, participant_id):
    data = {'ca_project': project_id, 'ca_type': 'default', 'ca_participant': participant_id}
    json_data = post_request('/api/calibrations', data)
    return json_data['ca_id']


def start_calibration(calibration_id):
    post_request('/api/calibrations/' + calibration_id + '/start')


def create_recording(participant_id):
    data = {'rec_participant': participant_id}
    json_data = post_request('/api/recordings', data)
    return json_data['rec_id']


def start_recording(recording_id):
    post_request('/api/recordings/' + recording_id + '/start')


def stop_recording(recording_id):
    post_request('/api/recordings/' + recording_id + '/stop')
