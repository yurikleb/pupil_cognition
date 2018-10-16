import board
import busio
import time
import digitalio

import adafruit_tsl2561

led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

# Initialize I2C and sensor.
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tsl2561.TSL2561(i2c)

# Main loop runs forever printing lux every second.
while True:
    #print('Lux: {}'.format(sensor.lux))
    print('{}'.format(sensor.lux))
    time.sleep(1.0)
    led.value = not led.value