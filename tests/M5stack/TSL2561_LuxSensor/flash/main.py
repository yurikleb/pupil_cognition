# A smaple code using the Adafruit tsl2561 Lux sensor on the m5stack

from m5stack import lcd
from tsl2561 import *
from machine import I2C, Pin
import time

lcd.clear()
lcd.setCursor(0, 0)
lcd.setColor(lcd.WHITE)
lcd.print('Connecting to sensor...\n')

i2c = I2C(sda=21, scl=22, freq=20000)
# i2cAddr = i2c.scan()

sensor = TSL2561(i2c)
sensor.active(True)
time.sleep_ms(500)

while True:
    lcd.clear()
    lcd.setCursor(0, 0)
    sensorVal = sensor.read()
    lcd.print("Lux: {} \n".format(sensorVal))
    print("Lux: {} \n".format(sensorVal))    
    time.sleep_ms(1000)