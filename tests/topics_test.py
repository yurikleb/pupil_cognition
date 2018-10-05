import zmq, msgpack
from zmq_tools import Msg_Receiver
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
topic = 'notify.meta.should_doc'
payload = msgpack.dumps({'subject':'meta.should_doc'})
requester.send_string(topic, flags=zmq.SNDMORE)
requester.send(payload)
requester.recv_string()

# wait and print responses
while True:
    # receiver is a Msg_Receiver, that returns a topic/payload tuple on recv()
    topic, payload = receiver.recv()
    actor = payload.get('diameter_3d')
    doc = payload.get('doc')
    print('%s: %s'%(actor,doc))