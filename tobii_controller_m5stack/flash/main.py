# A Controller to create projects recordings on the Tobii Glasses Pro Eye tracker

# microPython of "urllib.request" version is "urequests"
# https://github.com/micropython/micropython-lib/blob/master/urequests/urequests.py

# from machine import I2C, Pin
# from tsl2561 import *
from m5stack import lcd
import json
import time
import urequests
import socket


GLASSES_IP = "192.168.71.50"  # IPv4 address
PORT = 49152
base_url = 'http://' + GLASSES_IP
timeout = 1

def post_request(api_action, the_data=None):
    url = base_url + api_action
    the_data = json.dumps(the_data)
    response = urequests.request("POST", url, the_data.encode(), headers={"Content-Type": "application/json"})
    json_data = json.loads(response.content)
    return json_data

    # print(response.content)
    # lcd.print("RESPONSE: {} \n".format(response.content))

def wait_for_status(api_action, key, values):
    url = base_url + api_action
    running = True
    json_data = None

    while running:
        response = urequests.request("GET", url, headers={"Content-Type": "application/json"})
        print(response.content)
        json_data = json.loads(response.content)
        if json_data[key] in values:
            running = False
        time.sleep(1)

    return json_data[key]


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


if __name__ == "__main__":

    time.sleep_ms(1000)

    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.setColor(lcd.WHITE)

    main_running = True
    peer = (GLASSES_IP, PORT)

    try:
        project_id = create_project()
        print("project ID created: {} ".format(project_id))

        participant_id = create_participant(project_id)
        print("participant id created: {} ".format(participant_id))

        calibration_id = create_calibration(project_id, participant_id)
        print("calibration id created: {}".format(calibration_id))

        print("Project: " + project_id, ", Participant: ", participant_id, ", Calibration: ", calibration_id, " ")
        lcd.print("Project: {} \n Participant: {} \n Calibration: {} ".format(project_id, participant_id, calibration_id,))

        input_var = input("Press enter to calibrate")

        start_calibration(calibration_id)
        print('Calibration started...')
        status = wait_for_status('/api/calibrations/' + calibration_id + '/status', 'ca_state', ['failed', 'calibrated'])

        if status == 'failed':
            print('Calibration failed, using default calibration instead')
        else:
            print('Calibration successful')

        recording_id = create_recording(participant_id)
        print('Recording started...')

        start_recording(recording_id)
        time.sleep(5)
        stop_recording(recording_id)

        status = wait_for_status('/api/recordings/' + recording_id + '/status', 'rec_state', ['failed', 'done'])
        if status == 'failed':
            print('Recording failed')
        else:
            print('Recording successful')


    except Exception as e:
        print("Error")
        print(str(e))

    main_running = False
