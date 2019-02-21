#!/usr/bin/python
#This script was authored by AndrewH7 and belongs to him (www.instructables.com/member/AndrewH7)
#You have permission to modify and use this script only for your own personal usage
#You do not have permission to redistribute this script as your own work
#Use this script at your own risk

import RPi.GPIO as GPIO
import os
import time

shutdown_button = 37
power_led = 35
poweroff_time = 10 

#Replace YOUR_CHOSEN_GPIO_NUMBER_HERE with the GPIO pin number you wish to use
#Make sure you know which rapsberry pi revision you are using first
#The line should look something like this e.g. "shutdown_button=7"

GPIO.setmode(GPIO.BOARD)
#Use BCM pin numbering (i.e. the GPIO number, not pin number)


GPIO.setup(shutdown_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#It's very important the pin is an input to avoid short-circuits
#The pull-up resistor means the pin is high by default

# turn on the power indicator 
GPIO.setup(power_led, GPIO.OUT)
GPIO.output(power_led, True)

try:
    #Use falling edge detection to see if pin is pulled 
    GPIO.wait_for_edge(shutdown_button, GPIO.FALLING)

    #Send command to system to shutdown
    os.system("sudo shutdown -h now")

    # wait to turn off the LED, otherwize the cleanup will turn this off right away  
    time.sleep(poweroff_time) 

except KeyboardInterrupt:
    print "User terminated"

except:
    # this catches ALL other exceptions including errors.
    print "Other error or exception occurred!"

finally:
    GPIO.output(power_led, False)
    GPIO.cleanup()
    #Revert all GPIO pins to their normal states (i.e. input = safe)
