'''
    
    Small Communication test, to see how many "pupil size" packets arrived with a certain amount of time.


    Based on original Tobbi example file and modified for Python3:

    FileExample for how to create a project, participant, calibration and recording.
    In order to make the calibration pass the keep-alive messages needs to be sent.

    Note: This example program is tested with Python 2.7 on Ubuntu 12.04 LTS (precise),
          Ubuntu 14.04 LTS (trusty), and Windows 8.
'''

import urllib
import json
import time
# import threading
import socket

# import threading
from threading import Thread

GLASSES_IP = "192.168.71.50"  # IPv4 address
PORT = 49152
base_url = 'http://' + GLASSES_IP
timeout = 3

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
    while running:
        socket.sendto(msg.encode(), peer)
        time.sleep(timeout)


def post_request(api_action, data=None):
    url = base_url + api_action
    req = urllib.Request(url)
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(data)
    response = urllib.urlopen(req, data)
    data = response.read()
    json_data = json.loads(data)
    return json_data


def wait_for_status(api_action, key, values):
    url = base_url + api_action
    while running:
        req = urllib.Request(url)
        req.add_header('Content-Type', 'application/json')
        response = urllib.urlopen(req, None)
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

def send_event():
    try:
        print("Sending event...")
        data = {'ets': 0, 'type': 'BigEvent', 'tag': 0
        }
        url = base_url + '/api/events'
        req = urllib.Request(url)
        req.add_header('Content-Type', 'application/json')
        response = urllib.urlopen(req, json.dumps(data))
    except Exception as e:
        print("Error Posting: " + str(e))

def get_tracker_data(streamed_data_socket):

    print("Get Tracker Data Thread Started!")
    
    while running:         
        try:
            data, address = streamed_data_socket.recvfrom(1024)
            json_data = json.loads(data.decode())
            
            # Get Pupil Values
            if ('pd' in json_data):
    
                # Reset the all data arrays if pupil record limit is reached
                # if ((len(self.pupil_values["d_right"]) >= self.recLength) or  
                #     (len(self.pupil_values["d_left"]) >= self.recLength) ):
                    
                #     self.pupil_values["d_left"] = []
                #     self.pupil_values["d_right"] = []
                #     self.sensor_values = []
                #     self.osc_values = []

                pupilSize = json_data['pd']

                if (json_data['eye'] == "right"):
                    pupil_values["d_right"].append(pupilSize)
                elif (json_data['eye'] == "left"):
                    pupil_values["d_left"].append(pupilSize)
                
                # self.pupilLog.text = 'Pupil Size: \nL:%s \nR:%s'%(self.pupil_values["d_left"][-1],self.pupil_values["d_right"][-1])
                print(json_data)

                # Store latest incoming pupil size value
            
            # Get Tracker recorder updates
            # if ('notify.recording' in topic):
                
            #     if(topic == 'notify.recording.started'):
            #         self.start()

            #     if(topic == 'notify.recording.stopped'):
            #         self.stop()

        except Exception as e:
            print("Can't parse Tracker data")
            print(str(e))


    print("Tracker Data Reading Thread Stopped!")    

if __name__ == "__main__":
    global running
    running = True

    global pupil_values
    pupil_values = {"d_left" : [], "d_right": []}
    
    peer = (GLASSES_IP, PORT)

    try:
        # Create socket which will send a keep alive message for the live data stream
        data_socket = mksock(peer)

        try:
            td_thread = Thread(target = send_keepalive_msg, args=(data_socket, KA_DATA_MSG, peer,))
            td_thread.daemon = True
            td_thread.start()
        except Exception as e:
            print(str(e))

        try:
            get_tracker_data_thread = Thread(target = get_tracker_data, args = (data_socket,))
            get_tracker_data_thread.daemon = True
            get_tracker_data_thread.start()
        except Exception as e:
            print(str(e))


        # # Create socket which will send a keep alive message for the live video stream
        # video_socket = mksock(peer)
        # tv = threading.Timer(0, send_keepalive_msg, [video_socket, KA_VIDEO_MSG, peer])
        # tv.start()

        # project_id = create_project()
        # participant_id = create_participant(project_id)
        # calibration_id = create_calibration(project_id, participant_id)

        # print "Project: " + project_id, ", Participant: ", participant_id, ", Calibration: ", calibration_id, " "

        # input_var = raw_input("Press enter to calibrate")
        # print ('Calibration started...')
        # start_calibration(calibration_id)
        # status = wait_for_status('/api/calibrations/' + calibration_id + '/status', 'ca_state', ['failed', 'calibrated'])

        # if status == 'failed':
        #     print ('Calibration failed, using default calibration instead')
        # else:
        #     print ('Calibration successful')

        # recording_id = create_recording(participant_id)
        # print ('Recording started...')
        # start_recording(recording_id)

        
        time.sleep(timeout)
        # print(pupil_values)
        print(len(pupil_values["d_left"]))
        print(len(pupil_values["d_right"]))        
        # send_event()
        # time.sleep(3)
        
        # stop_recording(recording_id)
        # status = wait_for_status('/api/recordings/' + recording_id + '/status', 'rec_state', ['failed', 'done'])
        # if status == 'failed':
        #     print ('Recording failed')
        # else:
        #     print ('Recording successful')
    except:
        print("Error")

    running = False
