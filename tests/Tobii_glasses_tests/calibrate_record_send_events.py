"""
    Example for how to create a project, participant, calibration and recording.
    In order to make the calibration pass the keep-alive messages needs to be sent.

    Note:
    Adapted and tested on Python 3.6 by Yurikleb from original example provided by Tobii
    Also added a function that sends an external event to the glasses (See page 21 in the API Doc).
"""

import urllib.request
import json
import time
from threading import Thread
import socket

GLASSES_IP = "192.168.71.50"  # IPv4 address
PORT = 49152
base_url = 'http://' + GLASSES_IP
timeout = 1

# Keep-alive message content used to request live data and live video streams
KA_DATA_MSG = "{\"type\": \"live.data.unicast\", \"key\": \"some_GUID\", \"op\": \"start\"}"
KA_VIDEO_MSG = "{\"type\": \"live.video.unicast\", \"key\": \"some_other_GUID\", \"op\": \"start\"}"


# Create UDP socket
def mksock(peer):
    iptype = socket.AF_INET
    if ':' in peer[0]:
        iptype = socket.AF_INET6
    return socket.socket(iptype, socket.SOCK_DGRAM)


# Callback function
def send_keepalive_msg(socket, msg, peer):
    # global running
    while running:
        socket.sendto(msg.encode(), peer)
        time.sleep(timeout)


def post_request(api_action, data=None):
    url = base_url + api_action
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(data)
    response = urllib.request.urlopen(req, data.encode())
    data = response.read()
    json_data = json.loads(data)
    return json_data


def wait_for_status(api_action, key, values):
    url = base_url + api_action
    running = True
    while running:
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(req, None)
        data = response.read()
        json_data = json.loads(data)
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


def send_event(evtType, evtTag):
    try:
        print("Sending event...")
        data = {'ets': 0, 'type': evtType, 'tag': evtTag}
        url = base_url + '/api/events'
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(req, (json.dumps(data)).encode())
    except Exception as e:
        print("Error Posting: " + str(e))


if __name__ == "__main__":

    running = True

    peer = (GLASSES_IP, PORT)

    try:
        # Create socket which will send a keep alive message for the live data stream
        data_socket = mksock(peer)
        print(data_socket)

        try:
            td_thread = Thread(target=send_keepalive_msg, args=(data_socket, KA_DATA_MSG, peer,))
            td_thread.daemon = True
            td_thread.start()
        except Exception as e:
            print(str(e))

        # Create socket which will send a keep alive message for the live video stream
        video_socket = mksock(peer)
        try:
            tv_thread = Thread(target=send_keepalive_msg, args=(video_socket, KA_VIDEO_MSG, peer,))
            tv_thread.daemon = True
            tv_thread.start()
        except Exception as e:
            print(str(e))

        print("Sockets open!")

        # # Create socket which will send a keep alive message for the live data stream
        # data_socket = mksock(peer)
        # td = threading.Timer(0, send_keepalive_msg, [data_socket, KA_DATA_MSG, peer])
        # td.start()

        # # Create socket which will send a keep alive message for the live video stream
        # video_socket = mksock(peer)
        # tv = threading.Timer(0, send_keepalive_msg, [video_socket, KA_VIDEO_MSG, peer])
        # tv.start()

        project_id = create_project()
        print("project id created")
        participant_id = create_participant(project_id)
        print("participant id created")
        calibration_id = create_calibration(project_id, participant_id)
        print("calibration id created")
        print("Project: " + project_id, ", Participant: ", participant_id, ", Calibration: ", calibration_id, " ")

        input_var = input("Press enter to calibrate")
        print('Calibration started...')
        start_calibration(calibration_id)
        status = wait_for_status('/api/calibrations/' + calibration_id + '/status', 'ca_state',
                                 ['failed', 'calibrated'])

        if status == 'failed':
            print('Calibration failed, using default calibration instead')
        else:
            print('Calibration successful')

        recording_id = create_recording(participant_id)
        print('Recording started...')
        start_recording(recording_id)

        # Sending External Events
        eventType = 'luxVal'
        eventTag = '12.08'  # can be json (see API docs page 21)
        time.sleep(2)
        send_event(eventType, eventTag)
        time.sleep(2)
        send_event(eventType, eventTag)
        time.sleep(2)

        stop_recording(recording_id)
        status = wait_for_status('/api/recordings/' + recording_id + '/status', 'rec_state', ['failed', 'done'])
        if status == 'failed':
            print('Recording failed')
        else:
            print('Recording successful')

    except Exception as e:
        print("Error")
        print(str(e))

    running = False
