# Pupil Cognition (Project ConciousLi)

This is a collection of scripts used for the Pupil Cognition platform.

## Getting Started

This repo contains:
* Scripts which read sensor data (such as the TSL2561 Lux Sensor).
* Scripts intefacing with various eye trackers such as the Tobii Glasses Pro and the Pupil-Labs Tracker.
* Various versions or a RecorderApp to capture 
* R scripts to analyze the data captured 



### Prerequisites

Coming Soon

```
code examples go here
```

### Installing

Coming soon...

```
code examples go here
```


## Notes to Self

List of things and links to useful resources

### Communicating with Boards via Serial on Ubuntu:

On Ubuntu 17.0 and above all the needed drivers shoudl be pre installed.
If using one of the adafruit Boards with MicroPython or Circuit Python [follow the tutorial](https://learn.adafruit.com/welcome-to-circuitpython/advanced-serial-console-on-mac-and-linux)

Adafruit Boards address is usually:
* /dev/ttyACM0
* /dev/ttyACM1

M5STACK address is usually
* /dev/ttyUSB0
* /dev/ttyUSB1

To list serial devices open terminal and type one of the below:

```
ls /dev/ttyACM*
ls /dev/ttyUSB*
```

To Connect to the board serial console (Micro/Circuit-Python REPL):
```
screen /dev/ttyUSB0 115200
screen /dev/ttyACM0 115200
```

If getting a "[screen is terminating]" message, try running screen with sudo

[Full instructions how to use the MicroPython REPL](http://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#repl-over-the-serial-port)

To manage files on a MicroPython board (browse, upload, etc..) use ampy: 
```
export AMPY_PORT=/dev/ttyUSB0
ampy ls /flash/
```

### Other Micro Python Tools
+ [Mu Editor](https://github.com/mu-editor/mu)
+ [MU ESP-Mode](https://github.com/dybber/mu/tree/esp-mode)
+ [Thonny IDE](https://bitbucket.org/plas/thonny/wiki/MicroPython)
+ [Adafruit MicroPython Tool (ampy) - Interact with a MicroPython board over serial](https://github.com/adafruit/ampy)

