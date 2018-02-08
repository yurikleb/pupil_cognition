import csv
import serial
import time
import zmq, msgpack
from zmq_tools import Msg_Receiver


#Connect to Lux Sensor on Adafruit feather runing CircuitPython via 
ser = serial.Serial('/dev/ttyACM1', 115200, timeout=2)
print("connected to: " + ser.name)

#Setup ZMQ to get pupil data
ctx = zmq.Context()
ip = 'localhost' #If you talk to a different machine use its IP.
port = 50020 #The port defaults to 50020 but can be set in the GUI of Pupil Capture.

# open Pupil Remote socket
requester = ctx.socket(zmq.REQ)
requester.connect('tcp://%s:%s'%(ip,port))
requester.send_string('SUB_PORT')
ipc_sub_port = requester.recv_string()

# setup message receiver
sub_url = 'tcp://%s:%s'%(ip,ipc_sub_port)
receiver = Msg_Receiver(ctx, sub_url, topics=('pupil.0',))

# construct message
# topic = 'notify.meta.should_doc'
# payload = msgpack.dumps({'subject':'meta.should_doc'})
# requester.send_string(topic, flags=zmq.SNDMORE)
# requester.send(payload)
# requester.recv_string()

data = [[],[]]


# wait and print responses
while True:
    pupilSize = 0
    luxValue = 0

    try:
     if (ser.inWaiting() > 0):
      line = ser.readline().strip()
      luxValue = float(line)
      print('Lux Value: %s'%(luxValue))

     # receiver is a Msg_Receiver, that returns a topic/payload tuple on recv()
     topic, payload = receiver.recv()
     pupilSize = payload.get('diameter_3d')
     print('Pupil Size: %s'%(pupilSize))

     data[0].append(pupilSize)
     data[1].append(luxValue)

    except:
     print("oops cant parse data")

    #break when data limit reached
    if (len(data[0]) > 1000):
     break


#Save Data to CSV
print(data)
with open('datalog.csv','w') as newFile:
     newFileWriter = csv.writer(newFile)
     newFileWriter.writerow(data[0])
     newFileWriter.writerow(data[1])
