import sys
from os.path import basename
from time import sleep
from datetime import datetime
from pytz import timezone
from gpiozero import DistanceSensor  # this library uses BCM numbering for the Pi's pins
import csv

#from filters import Filter
import filters


# This function is going to be executed in a separate thread (process?), it makes and stores the distance measurements of the ultrasonic sensors
def thread_log(pwm, pwmLeft, pwmRight, trimFactorLeft, trimFactorRight, Lx, Ly):
    # Initialize the log file's name
    scriptBasename = basename(sys.argv[0])
    logDate = ((timezone('America/Sao_Paulo')).localize(datetime.now())).strftime('_%d-%m-%Y_%H-%M-%S')
    logfileName = scriptBasename + logDate + '.csv'

    # Instantiate the sensor's objects
    frontSensor = DistanceSensor(echo=23, trigger=24, max_distance=3)
    leftSensor = DistanceSensor(echo=25, trigger=8, max_distance=3)
    rightSensor = DistanceSensor(echo=17, trigger=27, max_distance=3)

    log_columns = ["gamepadLx", "gamepadLy", "frontSensor", "rightSensor", "leftSensor", "pwm", "pwmLeft", "pwmRight"]
    with open(logfileName, 'ab') as arquivo:
        logger = csv.writer(arquivo)
        logger.writerow(log_columns)

    # Initialize the filters for the distance measured
    frontSensorFilter = filters.MedianFilter(15)
    rightSensorFilter = filters.MedianFilter(15)
    leftSensorFilter = filters.MedianFilter(15)

    # Main loop
    while(True):
        frontSensorFilter.add_reading((frontSensor.distance*100))
        rightSensorFilter.add_reading((rightSensor.distance*100))
        leftSensorFilter.add_reading((leftSensor.distance*100))
        log = [float(Lx.value), float(Ly.value), frontSensorFilter.get_reading(), rightSensorFilter.get_reading(), leftSensorFilter.get_reading(), pwm.value, (pwmLeft.value * (1 - trimFactorLeft.value)), (pwmRight.value * (1 - trimFactorRight.value))]
        #log = [float(Lx.value), float(Ly.value), (frontSensor.distance*100), (rightSensor.distance*100), (leftSensor.distance*100), pwm.value, (pwmLeft.value * (1 - trimFactorLeft.value)), (pwmRight.value * (1 - trimFactorRight.value))]
        print(log)

        with open(logfileName, 'ab') as arquivo:
            logger = csv.writer(arquivo)
            logger.writerow(log)

        #sleep(0.0625) # 16hz
        sleep(0.015625) # 64hz
        #sleep(0.0078125) # 128hz
