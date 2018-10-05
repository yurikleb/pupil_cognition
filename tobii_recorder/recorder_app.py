#An App for recording data incoming from Pupil Eye Tracker
import kivy
kivy.require('1.10.0')
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.garden.graph import MeshLinePlot
from kivy.properties import *
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.config import ConfigParser
from kivy.uix.settings import *


import argparse
from pythonosc import dispatcher
from pythonosc import osc_server

import time
# import threading
from threading import Thread

import csv
import serial
import json
import socket
import sys

config = ConfigParser()
config.read('config.ini')



class Recorder(BoxLayout):

    eyeTrackerStatus = OptionProperty("Disconnected", options=["Connected", "Disconnected", "Connecting"])
    oscStatus = OptionProperty("Disconnected", options=["Connected", "Disconnected", "Connecting"])
    serStatus = OptionProperty("Disconnected", options=["Connected", "Disconnected", "Connecting"])        
    recLength = NumericProperty(config.get('Recorder', 'rec_samples'))

    pupil_values = {"d_left" : [], "d_right": []}
    osc_values = []
    sensor_values = []
    
    last_pupil_plot_Values = []
    last_sensor_plot_Values = []
    last_osc_plot_Values = []

    startTime = time.time()
    isRecording = False

    def __init__(self,**kwargs):

        super(Recorder, self).__init__(**kwargs)
        Window.size = (1000, 800)
        
        #Plots settings        
        self.plot_r_pupil = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot_l_pupil = MeshLinePlot(color=[0, 1, 0, 1])
        self.plot_sensor = MeshLinePlot(color=[0, 1, 0, 1])
        self.plot_osc = MeshLinePlot(color=[1, .5, .5, 1])


    # Create UDP socket
    def mksock(self, peer):
        iptype = socket.AF_INET
        if ':' in peer[0]:
            iptype = socket.AF_INET6
        return socket.socket(iptype, socket.SOCK_DGRAM)

    # Keep Communication with Tobii Alive
    def send_keepalive_msg(self, socket, msg, peer):

        timeout = 1.0
        
        while self.eyeTrackerStatus == "Connected" or self.eyeTrackerStatus == "Connecting":
            print("Sending " + msg + " to target " + peer[0] + " socket no: " + str(socket.fileno()) + "\n")
            socket.sendto(msg.encode(), peer)
            time.sleep(timeout)

        print("Keep Tracker connection alive thread stopped!")


    def eye_tracker_connect(self):
        
        self.eyeTrackerStatus = "Connecting"
        
        # Setup a Socket to get data from the Tracker

        GLASSES_IP = config.get('EYETRACKER', 'trk_addr')
        PORT = 49152 #config.get('EYETRACKER', 'trk_port') 

        # Keep-alive message content used to request live data
        KA_DATA_MSG = "{\"type\": \"live.data.unicast\", \"key\": \"some_GUID\", \"op\": \"start\"}"
        peer = (GLASSES_IP, PORT)

        # ('192.168.71.50', 49152)
        
        try:
            #Create socket which will send a keep alive message for the live data stream
            print(peer)
            data_socket = self.mksock(peer)
            self.td_thread = Thread(target = self.send_keepalive_msg, args=(data_socket, KA_DATA_MSG, peer,))
            self.td_thread.daemon = True
            self.td_thread.start()

            print("Connected to Eye Tracker")
            self.eyeTrackerStatus = "Connected"
            self.pupilLog.text = "Waiting for Data..."
            self.zmqConnectBtn.disabled = True        
        except Exception as e:
            self.eyeTrackerStatus = "Disconnected"
            print("Could not connect to Eye Tracker")
            print(str(e))
            self.pupilLog.text = "Could not Connect"

        #Start data reading thread    
        if (self.eyeTrackerStatus == "Connected"):
            self.get_tracker_data_thread = Thread(target = self.get_tracker_data, args = (data_socket,))
            self.get_tracker_data_thread.daemon = True
            self.get_tracker_data_thread.start()



    def get_tracker_data(self, streamed_data_socket):

        print("Get Tracker Data Thread Started!")
        
        while self.eyeTrackerStatus == "Connected":           
            try:
                data, address = streamed_data_socket.recvfrom(1024)
                json_data = json.loads(data.decode())
                
                # Get Pupil Values
                if ('pd' in json_data):
        
                    # Reset the all data arrays if pupil record limit is reached
                    if ((len(self.pupil_values["d_right"]) >= self.recLength) or  
                        (len(self.pupil_values["d_left"]) >= self.recLength) ):
                        
                        self.pupil_values["d_left"] = []
                        self.pupil_values["d_right"] = []
                        self.sensor_values = []
                        self.osc_values = []

                    pupilSize = json_data['pd']

                    if (json_data['eye'] == "right"):
                        self.pupil_values["d_right"].append(pupilSize)
                    elif (json_data['eye'] == "left"):
                        self.pupil_values["d_left"].append(pupilSize)
                    
                    self.pupilLog.text = 'Pupil Size: \nL:%s \nR:%s'%(self.pupil_values["d_left"][-1],self.pupil_values["d_right"][-1])
                    # print(json_data)

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


    def serial_connect(self):
        
        # Connect to Srial get data from sensors 
        # Such as a Lux Sensor on Adafruit feather runing CircuitPython
        # Serial settings tutorial here:
        # https://learn.adafruit.com/welcome-to-circuitpython/advanced-serial-console-on-mac-and-linux
        
        portAdr = config.get('SERIAL', 'serial_port')
        baudRate = config.get('SERIAL', 'serial_baud_rate')
        self.serStatus = "Connecting"

        try:
            # ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
            ser = serial.Serial(portAdr, baudRate, timeout=2)            
            
            print("connected to: " + ser.name)
            self.serStatus = "Connected"
            self.serLog.text = "Waiting for Data..."
            self.serConnectBtn.disabled = True            
        except:
            self.serStatus = "Disconnected"
            print("No Serial Found")
            self.serLog.text = "Could Not Connect"

        #Start data reading thread    
        if (self.serStatus == "Connected"):
            self.get_ser_data_thread = Thread(target = self.get_serial_data, args=(ser,))
            self.get_ser_data_thread.daemon = True
            self.get_ser_data_thread.start()


    def get_serial_data(self,ser):
        
        print("SERIAL Thread Started, Getting Data!")
        sensorValue = 0.0

        while self.serStatus == "Connected":
            try:
                if (ser != 0 and ser.inWaiting() > 0):
                    line = ser.readline().strip()
                    sensorValue = float(line)
                    
                    vals = (len(self.pupil_values["d_right"]), sensorValue)
                    self.sensor_values.append(vals)
                    
                    self.serLog.text = 'Lux Sensor Value: %s'%(sensorValue)
                    # print('Lux Sensoer Value: %s'%(sensorValue))           
                    # print(self.sensor_values)
            except:
                print("Can't parse SERIAL data")
                self.serStatus == "Disconnected"
            

        print("SERIAL Data Reading Thread Stopped!")

    
    def osc_connect(self):
      #Starts an OSC Server to get events data
      
      ip = config.get('OSC', 'osc_addr') #If you talk to a different machine use its IP.
      port = int(config.get('OSC', 'osc_port')) #The port defaults to 50020 but can be set in the GUI of Pupil Capture.
      
      try:
        
        dispt = dispatcher.Dispatcher()
        dispt.map("/event", self.osc_handler)

        self.osc_ser = osc_server.ThreadingOSCUDPServer((ip, port), dispt)
        self.osc_server_thread = Thread(target=self.osc_ser.serve_forever)
        self.osc_server_thread.daemon = True
        self.osc_server_thread.start()

        print("Serving on {}".format(self.osc_ser.server_address))      
        self.oscStatus = "Connected"
        self.oscLog.text = "Waiting for Data..."
        self.oscConnectBtn.disabled = True          

      except:
        self.oscStatus = "Disconnected"
        print("Could not start OSC")
        self.oscLog.text = 'Could not Satrt OSC \nPort %s might be busy'%(port)


    def osc_handler(self, addr, args):
      try:
        self.oscLog.text = '%s: %s'%(addr, args)
        vals = (len(self.pupil_values["d_right"]), args)
        self.osc_values.append(vals)
        # print('OSC messege on: %s: %s'%(addr, args))
      except ValueError: pass

    def plot_pupil_values(self, dt):
        #Plot the values stored in pupil_values{}
        if(len(self.pupil_values["d_right"]) < self.recLength):
            self.plot_r_pupil.points = [(i, j) for i, j in enumerate(self.pupil_values["d_right"])]
            self.plot_l_pupil.points = [(i, j) for i, j in enumerate(self.pupil_values["d_left"])]
            self.plot_sensor.points = [(i, j) for i, j in self.sensor_values]
            self.plot_osc.points = [(i, j) for i, j in self.osc_values]
        else:
            self.stop()
    
    def start(self):

        # Start Plotting the Data on the Chart
        self.pupilDataGraph.add_plot(self.plot_r_pupil)
        self.pupilDataGraph.add_plot(self.plot_l_pupil)
        self.sensorDataGraph.add_plot(self.plot_sensor)
        self.oscDataGraph.add_plot(self.plot_osc)
        
        self.pupil_values["d_right"] = []
        self.pupil_values["d_left"] = []
        self.osc_values = []
        self.sensor_values = []
        self.last_pupil_plot_Values = []
        self.last_sensor_plot_Values = []
        
        Clock.schedule_interval(self.plot_pupil_values, 0.001)
        self.startTime = time.time()
        
        self.isRecording = True
        self.recStopBtn.disabled = False
        
        print("Recording started")
    
    def stop(self):
        # Store the Latest Plot Values 
        self.last_pupil_plot_Values = list(enumerate(self.pupil_values["d_right"]))
        self.last_sensor_plot_Values = self.sensor_values
        self.last_osc_plot_Values = self.osc_values
        Clock.unschedule(self.plot_pupil_values)
        
        self.isRecording = False
        self.recStopBtn.disabled = True

        print("Recording Stopped")
        print("Recording Duration: %s sec"%(((time.time() - self.startTime))))
        print("Samples: %s"%(len(self.pupil_values["d_right"])))

    def save_data(self):
        print("Saving Datalogs CSV Files")
        SaveDialog(self.last_pupil_plot_Values, 
                    self.last_sensor_plot_Values,
                    self.last_osc_plot_Values).open()

    def quit_app(self):
        
        # self.osc_ser.shutdown()

        self.eyeTrackerStatus = "Disconnected"
        self.oscStatus = "Disconnected"        
        self.serStatus = "Disconnected"
        
        App.get_running_app().stop()
        Window.close()
        print("Closing App...")

        exit()

class SaveDialog(Popup):

    pupil_data = []
    sensor_data = []
    events_data = []

    def __init__(self, pup_data, sen_data, osc_data, **kwargs):  # my_widget is now the object where popup was called from.
        super(SaveDialog,self).__init__(**kwargs)
        
        self.pupil_data = pup_data
        self.sensor_data = sen_data
        self.events_data = osc_data
        
        self.fileNameBox.text = "SessionName"      

    
    def save_csv_file(self, fileName, dataValues):       
        with open('datalogs/%s_%s_%s.csv'%(int(time.time()), self.fileNameBox.text, fileName),'w', newline='') as newFile:
            newFileWriter = csv.writer(newFile)
            newFileWriter.writerows(dataValues)
            # print("Saved %s Data:"%(fileName))
            # print(dataValues)

    def save(self,*args):
        print ("Saving File...")
        self.save_csv_file("pupil", self.pupil_data)
        self.save_csv_file("lux", self.sensor_data)
        self.save_csv_file("evt", self.events_data)
        self.dismiss()


# MAIN APP WRAPPER CLASS
class RecorderApp(App):

    def on_stop(self):
        print('App Closed!')

    def build(self):
        return Recorder()

    def build_config(self, config):
        # Set the default values for the configs sections.
        # config.setdefaults('My Label', {'text': 'Hello', 'font_size': 20})
        pass
    
    def build_settings(self, settings):
        settings.add_json_panel('Recorder Settings', config, 'settings.json')
    
    def on_config_change(self, config, section, key, value):

        # Respond to changes in the configuration.

        Logger.info("recorder_app.py: App.on_config_change: {0}, {1}, {2}, {3}".format(
            config, section, key, value))

        if section == "Recorder":
            if key == "rec_samples":
                self.root.recLength = value
            # elif key == 'font_size':
            #     self.root.ids.label.font_size = float(value)

    def close_settings(self, settings=None):
        
        # The settings panel has been closed.
        
        Logger.info("recorder_app.py: App.close_settings: {0}".format(settings))
        super(RecorderApp, self).close_settings(settings)        



if __name__ == "__main__":
    # run app interface
    RecorderApp().run()