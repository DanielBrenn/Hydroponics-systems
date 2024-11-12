import RPi.GPIO as GPIO
import os
import time


BUTTON_GPIO = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

if True:
    GPIO.wait_for_edge(BUTTON_GPIO, GPIO.FALLING)
    os.system("sudo nmcli device disconnect wlan0")
    os.system("sudo nmcli device up wlan0")
    os.system("sudo nmcli device wifi hotspot ssid rpi4 password 12345678")
    GPIO.cleanup()
    