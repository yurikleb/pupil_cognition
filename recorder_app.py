#An App for recording data incoming from Pupil Eye Tracker
import kivy
kivy.require('1.10.0')
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.graph import MeshLinePlot
from kivy.properties import *
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.config import ConfigParser
from kivy.uix.settings import *

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
    recLength = NumericProperty()

    def __init__(self,**kwargs):

        Window.size = (1000, 800)
        self.recLength = config.get('Recorder', 'rec_samples')

        super(Recorder, self).__init__(**kwargs)

        #Plot settings        
        self.plot_pupil = MeshLinePlot(color=[1, 0, 0, 1])
        #self.data_graph.xmax = self.recLength
      
        #Connect to Lux Sensor on Adafruit feather runing CircuitPython via 
        # try:
        #     ser = serial.Serial('/dev/ttyACM1', 115200, timeout=2)
        #     print("connected to: " + ser.name)
        # except:
        #     print("No Serial Found")
        #     ser = 0 

        # Setup ZMQ to get pupil data
        self.is_running = True
        self.pupil_values = []
        
        try:
            ctx = zmq.Context()
            ip = 'localhost' #If you talk to a different machine use its IP.
            port = 50020 #The port defaults to 50020 but can be set in the GUI of Pupil Capture.

            #Open Pupil Remote socket
            #Using LINGER and Poller for Socket timeout
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

            # if connection is established setup message receiver
            sub_url = 'tcp://%s:%s'%(ip,ipc_sub_port)
            self.receiver = Msg_Receiver(ctx, sub_url, topics=('pupil.0',))
            self.zmqStatus = "Connected"
        
        except:
            self.zmqStatus = "Disconnected"
            self.receiver = False
            print("Could not connect to Pupil Service")

        #Start data reading thread    
        if (self.receiver):
            self.get_data_thread = Thread(target = self.get_data)
            self.get_data_thread.daemon = True
            self.get_data_thread.start()

    def get_value(self, dt):
        #Plot the values stored in pupil_values[]
        if( len(self.pupil_values) < self.recLength ):
            self.plot_pupil.points = [(i, j) for i, j in enumerate(self.pupil_values)]
        else:
            Clock.unschedule(self.get_value)

    def get_data(self):

        print("Getting Data")

        # global pupil_values

        while self.is_running == True:

            pupilSize = 0
            luxValue = 0

            try:
                # if (ser != 0 and ser.inWaiting() > 0):
                #     line = ser.readline().strip()
                #     luxValue = float(line)
                #     print('Lux Value: %s'%(luxValue))

                # receiver is a Msg_Receiver, that returns a topic/payload tuple on recv()
                topic, payload = self.receiver.recv()
                pupilSize = payload.get('diameter_3d')
                print('Pupil Size: %s'%(pupilSize))
                # data[0].append(pupilSize)
                # data[1].append(luxValue)
                # data[2].append(int((time.time() - startTime)*10000))

            except:
                print("oops cant parse data")


            val = pupilSize
            if len(self.pupil_values) >= self.recLength:
                self.pupil_values = []

            self.pupil_values.append(val)

        print("Data Read Stopped")
    
    def start(self):
        pass
        self.data_graph.add_plot(self.plot_pupil)
        Clock.schedule_interval(self.get_value, 0.001)

    def stop(self):
        Clock.unschedule(self.get_value)

    def quit_app(self):
        self.is_running = False
        App.get_running_app().stop()
        Window.close()
        print("Closing App...")


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

    print("###### PUPIL RECORDER #######")

    # run app interface
    RecorderApp().run()