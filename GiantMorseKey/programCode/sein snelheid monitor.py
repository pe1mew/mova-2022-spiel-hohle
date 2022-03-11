#!/usr/bin/env python3.9
import signal
import sys
import RPi.GPIO as GPIO
import time
global cnt
cnt=0
global lstcnt
lstcnt=0
global lstint
lstint=time.time()
global actint
actint=time.time()
global key
key=1
global kdt
kdt=time.time()
global kut
kut=time.time()


BUTTON_GPIO = 4

def button_callback(channel):
    global cnt
    global lstint
    global actint
    global key
    global kut
    global kdt


    actint=time.time()
    if actint - lstint > 0.05:
        lstint=actint
        if key==1:
            key=0
            kdt=lstint
        else:
            key=1
            kut=lstint
        cnt=cnt+1


GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BUTTON_GPIO, GPIO.BOTH,
callback=button_callback
                      #,bouncetime=100
                          )

while True:
    if cnt!=lstcnt:
        #print (cnt)
        #print (key)
        if cnt%2==1:
            print ("kul : %4.2f" % (kdt-kut))
        else:
            print ("kdl             : %4.2f" % (kut-kdt))
        lstcnt=cnt