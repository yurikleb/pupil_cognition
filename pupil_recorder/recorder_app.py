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
from threading import Thread

import zmq, msgpack
from zmq_tools import Msg_Receiver

import csv
import serial

config = ConfigParser()
config.read('config.ini')



class Recorder(BoxLayout):

    zmqStatus = OptionProperty("Disconnected", options=["Connected", "Disconnected", "Connecting"])
    oscStatus = OptionProperty("Disconnected", options=["Connected", "Disconnected", "Connecting"])
    serStatus = OptionProperty("Disconnected", options=["Connected", "Disconnected", "Connecting"])        
    recLength = NumericProperty(config.get('Recorder', 'rec_samples'))

    pupil_values = []
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
        
        #Plot settings        
        self.plot_pupil = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot_sensor = MeshLinePlot(color=[0, 1, 0, 1])
        self.plot_osc = MeshLinePlot(color=[1, .5, .5, 1])


    def zmq_connect(self):
        
        self.zmqStatus = "Connecting"
        
        # Setup ZMQ to get pupil data
        ctx = zmq.Context()
        ip = config.get('ZMQ', 'zmq_addr') #If you talk to a different machine use its IP.
        port = config.get('ZMQ', 'zmq_port') #The port defaults to 50020 but can be set in the GUI of Pupil Capture.

        try:

            #Open Pupil Remote socket
            #Using LINGER and POLLER for Socket timeout check
            requester = ctx.socket(zmq.REQ)        
            requester.setsockopt(zmq.LINGER, 0)
            requester.connect('tcp://%s:%s'%(ip,port))
            requester.send_string('SUB_PORT')
            poller = zmq.Poller()
            poller.register(requester, zmq.POLLIN)        
            if poller.poll(2*1000): # 2s timeout in milliseconds
                ipc_sub_port = requester.recv_string()
            else:
                raise IOError("Timeout processing socket auth quest")

            # If connection is established setup message receiver
            sub_url = 'tcp://%s:%s'%(ip,ipc_sub_port)
            # Subscribe to Pupil Data messegaes and recorder notifications
            self.receiver = Msg_Receiver(ctx, sub_url, topics=('pupil.0','notify.recording',))
            
            print("ZMQ connected")
            self.zmqStatus = "Connected"
            self.zmqLog.text = "Waiting for Data..."
            self.zmqConnectBtn.disabled = True            
        except:
            self.zmqStatus = "Disconnected"
            print("Could not connect to Pupil Service")
            self.zmqLog.text = "Could not Connect"

        #Start data reading thread    
        if (self.zmqStatus == "Connected"):
            self.get_zmq_data_thread = Thread(target = self.get_zmq_data)
            self.get_zmq_data_thread.daemon = True
            self.get_zmq_data_thread.start()


    def get_zmq_data(self):

        print("ZMQ Thread Started, Getting Data!")
        while self.zmqStatus == "Connected":           
            try:
                # receiver is a Msg_Receiver, that returns a topic/payload tuple on recv()
                topic, payload = self.receiver.recv()

                # Get Pupil Values
                if ('pupil' in topic):
                    pupilSize = payload.get('diameter_3d')
                    self.zmqLog.text = 'Pupil Size: %s'%(pupilSize)
                    # print('Pupil Size: %s'%(pupilSize))
        
                    # Reset the all data arrays if pupil record limit is reached
                    if (len(self.pupil_values) >= self.recLength):
                        self.pupil_values = []
                        self.sensor_values = []
                        self.osc_values = []

                    # Store latest incoming pupil size value
                    self.pupil_values.append(pupilSize)
                
                # Get Pupil recorder updates
                if ('notify.recording' in topic):
                    
                    if(topic == 'notify.recording.started'):
                        self.start()

                    if(topic == 'notify.recording.stopped'):
                        self.stop()
            except:
                print("Can't parse ZMQ data")


        print("ZQM Data Reading Thread Stopped!")


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
                    
                    vals = (len(self.pupil_values), sensorValue)
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
        vals = (len(self.pupil_values), args)
        self.osc_values.append(vals)
        # print('OSC messege on: %s: %s'%(addr, args))
      except ValueError: pass

    def plot_pupil_values(self, dt):
        #Plot the values stored in pupil_values[]
        if(len(self.pupil_values) < self.recLength):
            self.plot_pupil.points = [(i, j) for i, j in enumerate(self.pupil_values)]
            self.plot_sensor.points = [(i, j) for i, j in self.sensor_values]
            self.plot_osc.points = [(i, j) for i, j in self.osc_values]
        else:
            self.stop()
    
    def start(self):

        # Start Plotting the Data on the Chart
        self.pupilDataGraph.add_plot(self.plot_pupil)
        self.sensorDataGraph.add_plot(self.plot_sensor)
        self.oscDataGraph.add_plot(self.plot_osc)
        
        self.pupil_values = []
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
        self.last_pupil_plot_Values = list(enumerate(self.pupil_values))
        self.last_sensor_plot_Values = self.sensor_values
        self.last_osc_plot_Values = self.osc_values
        Clock.unschedule(self.plot_pupil_values)
        
        self.isRecording = False
        self.recStopBtn.disabled = True

        print("Recording Stopped")
        print("Recording Duration: %s sec"%(((time.time() - self.startTime))))
        print("Samples: %s"%(len(self.pupil_values)))

    def save_data(self):
        print("Saving Datalogs CSV Files")
        SaveDialog(self.last_pupil_plot_Values, 
                    self.last_sensor_plot_Values,
                    self.last_osc_plot_Values).open()

    def quit_app(self):
        
        # self.osc_ser.shutdown()

        self.zmqStatus = "Disconnected"
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