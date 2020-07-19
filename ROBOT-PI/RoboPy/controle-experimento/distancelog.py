import sys
from time import sleep
from os.path import basename
from datetime import datetime
from pytz import timezone
from gpiozero import DistanceSensor  # this library uses BCM numbering for the Pi's pins
import csv
from multiprocessing import Process
from ctypes import c_char_p

from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

#from filters import Filter
import filters
import numpy

# This function is going to be executed in a separate thread (process?), it makes and stores the distance measurements of the ultrasonic sensors
def thread_log(
    frequency,
    shared_variables,
    verbose=False
):

    # Initialize the log file's name
    scriptBasename = basename(sys.argv[0])
    logDate = ((timezone('America/Sao_Paulo')).localize(datetime.now())).strftime('_%d-%m-%Y_%H-%M-%S')
    logFileName = scriptBasename + logDate + '.csv'
    
    # Instantiate the sensor's objects
    frontSensor = DistanceSensor(echo=23, trigger=24, max_distance=3.0)
    leftSensor = DistanceSensor(echo=25, trigger=8, max_distance=3.0)
    rightSensor = DistanceSensor(echo=17, trigger=27, max_distance=3.0)

    log_columns = [
        "gamepadLx","gamepadLy",
        "frontSensor", "rightSensor", "leftSensor",
        "pwm", "pwmLeft", "pwmRight",
        "steerLeft", "steerRight",
        "ticksLeft", "ticksRight"
    ]
    
    with open(logFileName, 'ab') as arquivo:
        logger = csv.writer(arquivo)
        logger.writerow(log_columns)


    # Initialize the filters for the distance measured
    
    # medFrontSensorFilter = filters.MedianFilter(15)
    # medRightSensorFilter = filters.MedianFilter(15)
    # medLeftSensorFilter = filters.MedianFilter(15)

    # med2FrontSensorFilter = filters.MedianFilter(15)
    # med2RightSensorFilter = filters.MedianFilter(15)
    # med2LeftSensorFilter = filters.MedianFilter(15)

    # meaFrontSensorFilter = filters.MeanFilter(15)
    # meaRightSensorFilter = filters.MeanFilter(15)
    # meaLeftSensorFilter = filters.MeanFilter(15)

    # Main loop
    while(True):

        # medFrontSensorFilter.add_value((frontSensor.distance*100))
        # medRightSensorFilter.add_value((rightSensor.distance*100))
        # medLeftSensorFilter.add_value((leftSensor.distance*100))
        
        # med2FrontSensorFilter.add_value(medFrontSensorFilter.get_value())
        # med2RightSensorFilter.add_value(medRightSensorFilter.get_value())
        # med2LeftSensorFilter.add_value(medLeftSensorFilter.get_value())

        # meaFrontSensorFilter.add_value(med2FrontSensorFilter.get_value())
        # meaRightSensorFilter.add_value(med2RightSensorFilter.get_value())
        # meaLeftSensorFilter.add_value(med2LeftSensorFilter.get_value())
        
        # shared_variables['distF'].value = meaFrontSensorFilter.get_value()
        # shared_variables['distR'].value = meaRightSensorFilter.get_value()
        # shared_variables['distL'].value = meaLeftSensorFilter.get_value()
        
               
        shared_variables['distF'].value = frontSensor.distance*100
        shared_variables['distR'].value = rightSensor.distance*100
        shared_variables['distL'].value = leftSensor.distance*100

        log = [
            float(shared_variables['Lx'].value), float(shared_variables['Ly'].value),
            shared_variables['distF'].value, shared_variables['distR'].value, shared_variables['distL'].value,
            shared_variables['pwm'].value, shared_variables['pwmLeft'].value, shared_variables['pwmRight'].value,
            shared_variables['steerLeft'].value, shared_variables['steerRight'].value,
            shared_variables['ticksLeft'].value, shared_variables['ticksRight'].value
        ]

        if(verbose):
            print(log)

        with open(logFileName, 'ab') as arquivo:
            logger = csv.writer(arquivo)
            logger.writerow(log)

        sleep((1.0/frequency))
        shared_variables['time'].value = shared_variables['time'].value + 1.0/frequency