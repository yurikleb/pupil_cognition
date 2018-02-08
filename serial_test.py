import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2)

print("connected to: " + ser.name)

while True:
   line = ser.readline().strip()
   data = line.split()
   
   try:
   	#value = float(data[0])
   	value = float(line)
   	print(line)
   	print(value)
   except:
   	print("oops")



ser.close()