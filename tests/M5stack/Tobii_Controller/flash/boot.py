# This file is executed on every boot (including wake-boot from deepsleep)
import sys
sys.path[1] = '/flash/lib'
from m5stack import lcd, speaker, buttonA, buttonB, buttonC

# ---------- M5Cloud ------------
if True:
    if buttonB.isPressed():
        lcd.println('On: OFF-LINE Mode', color=lcd.ORANGE)
    else:
        import wifisetup

        # Uncomment the below line when working with online M5STACK cloud IDE
        # import m5cloud

