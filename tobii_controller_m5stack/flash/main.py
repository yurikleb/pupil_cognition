# A M5Stack Controller to create projects and recordings on the Tobii Glasses Pro Eye tracker
# As well as log sensor data.

from m5stack import *
from machine import I2C, Pin
from tsl2561 import *
import time
import tobii_glasses as tobii


project_id, participant_id, calibration_id, recording_id = '', '', '', ''
is_calibrated = False


def new_project():

    global project_id, participant_id

    try:
        project_id = tobii.create_project()
        print("project ID created: {} ".format(project_id))

        participant_id = tobii.create_participant(project_id)
        print("participant id created: {} ".format(participant_id))

        print("Project: ", project_id, ", Participant: ", participant_id)

    except Exception as e:
        print("Could Not Create new Project / Paticipant / Calibration:")
        print(str(e))


def calibrate():
    global calibration_id

    try:
        calibration_id = tobii.create_calibration(project_id, participant_id)
        print("calibration id created: {}".format(calibration_id))

        tobii.start_calibration(calibration_id)
        print('Calibration started...')
        status = tobii.wait_for_status('/api/calibrations/' + calibration_id + '/status', 'ca_state', ['failed', 'calibrated'])

        if status == 'failed':
            print('Calibration failed, using default calibration instead')
        else:
            print('Calibration successful')

    except Exception as e:
        print("Could Not Calibrate:")
        print(str(e))


def record():

    global recording_id

    try:
        recording_id = tobii.create_recording(participant_id)
        print('Recording Created...')

        tobii.start_recording(recording_id)
        print('Recording Started...')

        time.sleep(5)

        sensor_val = sensor.read()
        eventType = 'luxVal'
        # eventTag = '12.08'  # can be json (see Tobii Pro Glasses 2 API docs page 21)
        eventTag = str(sensor_val)
        print("Sending sensor value event...")
        tobii.send_event(eventType, eventTag)

        time.sleep(5)

        tobii.stop_recording(recording_id)

        status = tobii.wait_for_status('/api/recordings/' + recording_id + '/status', 'rec_state', ['failed', 'done'])
        if status == 'failed':
            print('Recording failed')
        else:
            print('Recording successful')

    except Exception as e:
        print("Could Not Record:")
        print(str(e))


def ui_init():
    lcd.clear()
    lcd.setColor(lcd.WHITE)
    lcd.setwin(0, 200, 106, 240)
    lcd.clearwin(lcd.DARKGREY)
    lcd.text(lcd.CENTER, lcd.CENTER, "CALIBRATE")
    lcd.setwin(213, 200, 320, 240)
    lcd.clearwin(lcd.DARKGREY)
    lcd.text(lcd.CENTER, lcd.CENTER, "RECORD")
    lcd.resetwin()
    lcd.setCursor(0, 0)


if __name__ == "__main__":

    time.sleep(1)

    # Connect to to TSL2561 Lux Sensor
    try:
        print("Connecting to TSL2561 via I2c...")
        lcd.print("Connecting to TSL2561 via I2c...")
        i2c = I2C(sda=21, scl=22, freq=20000)
        # i2cAddr = i2c.scan()
        sensor = TSL2561(i2c)
        sensor.active(True)
        print("Connected!")
        lcd.print("Connected!")
    except Exception as e:
        print("Could not connect:")
        print(str(e))

    time.sleep(1)

    ui_init()

    main_running = True
    new_project()
    lcd.print(" Project: {} \n Participant: {} \n ".format(project_id, participant_id))

    buttonA.wasReleased(calibrate)
    buttonC.wasReleased(record)

    main_running = False
