# A M5Stack Controller to create projects and recordings on the Tobii Glasses Pro Eye tracker
# As well as log sensor data.

from m5stack import *
import time, _thread
from machine import I2C, Pin
from tsl2561 import *
import network
import time
import network
import m5gui as gui
import tobii_glasses as tobii

wlan = network.WLAN(network.STA_IF)

i2c = I2C(sda=21, scl=22, freq=20000)
sensor_refresh_rate = 1000

tobii_recording = tobii.TobiiRecording()


def new_project():
    recording = tobii.TobiiRecording()

    if wlan.isconnected():
        try:
            recording.project_id = tobii.create_project()
            print("project ID created: {} ".format(recording.project_id))

            recording.participant_id = tobii.create_participant(recording.project_id)
            print("participant id created: {} ".format(recording.participant_id))

            print("Project: ", recording.project_id, ", Participant: ", recording.participant_id)

            return recording

        except Exception as e:
            print("Could Not Create new Project or Participant:")
            print(str(e))


def calibrate(recording):
    try:
        calibration_id = tobii.create_calibration(recording.project_id, recording.participant_id)
        print("calibration id created: {}".format(calibration_id))

        tobii.start_calibration(calibration_id)
        print('Calibration started...')
        status = tobii.wait_for_status('/api/calibrations/' + calibration_id + '/status',
                                       'ca_state', ['failed', 'calibrated'])

        if status == 'failed':
            print('Calibration failed, using default calibration instead')
        else:
            print('Calibration successful')

        return calibration_id

    except Exception as e:
        print("Could Not Calibrate:")
        print(str(e))


def start_record(recording):
    try:
        recording_id = tobii.create_recording(recording.participant_id)
        print('Recording Created...')

        tobii.start_recording(recording_id)
        print('Recording Started...')

        return recording_id

    except Exception as e:
        print("Could Not Start Recording:")
        print(str(e))


def stop_record(recording):
    try:
        print("Stopping recording")
        tobii.stop_recording(recording.recording_id)

        status = tobii.wait_for_status('/api/recordings/' + recording.recording_id + '/status',
                                       'rec_state', ['failed', 'done'])
        if status == 'failed':
            print('Recording failed')
        else:
            print('Recording successful')

    except Exception as e:
        print("Could Not Stop Recording:")
        print(str(e))


def get_sensor_data(refresh_rate):
    global tobii_recording
    is_sensor_connected = False

    # Connect to Sensor
    try:
        print("Connecting to TSL2561 via I2c...")
        gui.log_box.update("Connecting to TSL2561...")
        sensor = TSL2561(i2c)
        # i2cAddr = i2c.scan()
        sensor.active(True)
        is_sensor_connected = True
        sensor.gain = 0  # Set Low Gain Mode
        sensor.integration_time = 2  # Set 402ms integration time.
        print("Connected!")
        gui.log_box.update("Connected!\n")
    except Exception as e:
        print("Can't connect to Sensor:")
        gui.log_box.update("Can't Connect!\n")
        print(str(e))

    # Get sensor reading loop
    while is_sensor_connected:
        sensor_val = sensor.read()
        is_sensor_connected = sensor.active()
        gui.sensor_a_val_box.setText(str(round(sensor_val, 2)))

        if tobii_recording.is_recording:
            event_tag = str(sensor_val)  # event_tag can be json (see Tobii Pro Glasses 2 API docs page 21)
            print("Sending sensor value event...")
            tobii.send_event('luxVal', event_tag)

        time.sleep_ms(refresh_rate)


def connect_to_tobii():
    global wlan
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to Tobii Glasses...')
        wlan.connect('TG02B-080105004421', 'TobiiGlasses')
        while not wlan.isconnected():
            pass

    print('network config:', wlan.ifconfig())
    gui.log_box.update('Connected to Tobii: \nip: {} tobii ip: {} \n'.format(wlan.ifconfig()[0], wlan.ifconfig()[2]))
    gui.tobi_ip_box.setText(str(wlan.ifconfig()[0]))
    gui.tobii_status_box.setText("READY", lcd.GREEN)


if __name__ == "__main__":

    _thread.start_new_thread('SensorRead', get_sensor_data, (sensor_refresh_rate,))
    time.sleep(1)

    gui.log_box.update("Connecting to to Tobii... \n")
    gui.tobii_status_box.setText("Connecting...", lcd.GREEN)
    connect_to_tobii()
    time.sleep(1)

    main_running = True
    print("Waiting for input...")

    while main_running:

        if buttonA.wasReleased():
            gui.tobii_status_box.setText("Creating Project...")
            tobii_recording = new_project()
            gui.log_box.update("New project & participant created! \n"
                               "Project: {} \n"
                               "Participant: {} \n"
                               .format(tobii_recording.project_id, tobii_recording.participant_id))
            gui.tobii_project_val_box.setText(str(tobii_recording.project_id))
            gui.tobii_participant_val_box.setText(str(tobii_recording.participant_id))
            gui.tobii_status_box.setText("READY", lcd.GREEN)

        if buttonB.wasReleased():
            gui.tobii_status_box.setText("CALIBRATING", lcd.GREEN)
            tobii_recording.calibration_id = calibrate(tobii_recording)
            gui.log_box.update("Calibration ID:{} Done! \n".format(tobii_recording.calibration_id))
            gui.tobii_calibration_val_box.setText(str(tobii_recording.calibration_id))

            speaker.volume(2)
            speaker.tone(freq=1800)
            speaker.tone(freq=1800, duration=200)

            gui.tobii_status_box.setText("READY", lcd.GREEN)

        if buttonC.wasReleased():
            if not tobii_recording.is_recording:
                gui.tobii_status_box.setText("RECORDING", lcd.RED)
                tobii_recording.recording_id = start_record(tobii_recording)
                tobii_recording.is_recording = True
                gui.log_box.update("Recording ID:{} Started! \n".format(tobii_recording.recording_id))
            else:
                tobii_recording.is_recording = False
                stop_record(tobii_recording)
                gui.log_box.update("Recording ID:{} Done! \n".format(tobii_recording.recording_id))
                gui.tobii_status_box.setText("READY", lcd.GREEN)

        time.sleep(0.1)

    # buttonA.wasReleased(callback=new_project)
    # buttonB.wasReleased(callback=calibrate)
    # buttonC.wasReleased(callback=record)

    main_running = False
