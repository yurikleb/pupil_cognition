# A M5Stack Controller to create projects and recordings on the Tobii Glasses Pro Eye tracker
# As well as log sensor data.

from m5stack import *
from m5ui import *
import time, _thread
from machine import I2C, Pin
from tsl2561 import *
import network
import time
import tobii_glasses as tobii
import network

wlan = network.WLAN(network.STA_IF)

i2c = I2C(sda=21, scl=22, freq=20000)
sensor = TSL2561(i2c)
sensor_refresh_rate = 1000

tobii_recording = tobii.TobiiRecording()

lcd.clear()
btnA = M5Button(name='ButtonA', text='New', visibility=True)
btnB = M5Button(name='ButtonB', text='Calibrate', visibility=True)
btnC = M5Button(name='ButtonC', text=' REC', visibility=True)
luxValBox = M5TextBox(230, 0, "LUX", lcd.FONT_Default, 0xf4e542)
lcd.setCursor(0, 0)


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


def sensor_init():
    # Connect to to TSL2561 Lux Sensor
    global sensor

    try:
        print("Connecting to TSL2561 via I2c...")
        lcd.print("Connecting to TSL2561...")
        # i2cAddr = i2c.scan()
        sensor.active(True)
        sensor.gain = 0              # Set Low Gain Mode
        sensor.integration_time = 2  # Set 402ms integration time.
        print("Connected!")
        lcd.print("Connected!\n")
    except Exception as e:
        print("Could not connect:")
        lcd.print("Could Not Connect!\n")
        print(str(e))


def get_sensor_data():
    global sensor, luxValBox, tobii_recording

    sensor_init()

    while sensor.active():
        cursor_pos = lcd.getCursor()

        sensor_val = sensor.read()
        # sensor_val = round(sensor.read(),2)

        luxValBox.setText("Lux: {}".format(str(round(sensor_val, 2))))

        if tobii_recording.is_recording:
            event_tag = str(sensor_val)  # event_tag can be json (see Tobii Pro Glasses 2 API docs page 21)
            print("Sending sensor value event...")
            tobii.send_event('luxVal', event_tag)

        lcd.setCursor(cursor_pos[0], cursor_pos[1])
        time.sleep_ms(sensor_refresh_rate)


def connect_to_tobii():
    global wlan
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to Tobii Glasses...')
        wlan.connect('TG02B-080105004421', 'TobiiGlasses')
        while not wlan.isconnected():
            pass

    print('network config:', wlan.ifconfig())
    lcd.print('Connected to Tobii: \nip: {} tobii ip: {} \n'.format(wlan.ifconfig()[0], wlan.ifconfig()[2]))


if __name__ == "__main__":

    lcd.print("Connecting to to Tobii... \n")
    connect_to_tobii()
    time.sleep(1)

    _thread.start_new_thread('SensorRead', get_sensor_data, ())
    time.sleep(1)

    main_running = True
    print("Waiting for input...")

    while main_running:

        if buttonA.wasReleased():
            tobii_recording = new_project()
            lcd.print("NEW PROJECT & PARTICIPANT CREATED! \n"
                      "Project: {} \n"
                      "Participant: {} \n"
                      .format(tobii_recording.project_id, tobii_recording.participant_id))

        if buttonB.wasReleased():
            lcd.print("Calibrating...")
            tobii_recording.calibration_id = calibrate(tobii_recording)
            lcd.print("Claibration ID: {} Done! \n".format(tobii_recording.calibration_id))

        if buttonC.wasReleased():
            if not tobii_recording.is_recording:
                tobii_recording.recording_id = start_record(tobii_recording)
                tobii_recording.is_recording = True
                lcd.print("Recording ID:{} Started! \n".format(tobii_recording.recording_id))
            else:
                tobii_recording.is_recording = False
                stop_record(tobii_recording)
                lcd.print("Recording ID:{} Done! \n".format(tobii_recording.recording_id))

        time.sleep(0.1)

    # buttonA.wasReleased(callback=new_project)
    # buttonB.wasReleased(callback=calibrate)
    # buttonC.wasReleased(callback=record)

    main_running = False
