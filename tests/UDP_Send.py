import socket
import sys
import struct

UDP_IP = "192.168.27.74"
UDP_PORT = 2390
msg = "Hello, Sensor!"


# Create a UDP socket
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
# server_address = ('192.168.26.246', 10000)
# print('starting up on {} port {}'.format(*server_address))
# sock.bind(server_address)
    
print ("UDP target IP:", UDP_IP)
print ("UDP target port:", UDP_PORT)
print ("Message: ", msg)
   
# Create UDP socket
def mksock(peer):
    iptype = socket.AF_INET
    if ':' in peer[0]:
        iptype = socket.AF_INET6
    return socket.socket(iptype, socket.SOCK_DGRAM)


if __name__ == "__main__":

  peer = (UDP_IP, UDP_PORT)
  print(peer)

  # Create socket 
  data_socket = mksock(peer)

  # client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  data_socket.sendto(msg.encode('utf-8'), peer)
  data, addr = data_socket.recvfrom(1024)
  print(data)


  while True:
      print('\n\nwaiting to receive msg')
      data, address = data_socket.recvfrom(1024)

      print('received {} bytes from {}'.format(len(data), address))
      sensor_data = float(data.decode());
      print(sensor_data)
      
      # if data:
      #     sent = sock.sendto(data, address)
      #     print('sent {} bytes back to {}'.format(
      #         sent, address))