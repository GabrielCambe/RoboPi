#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.  

from evdev import InputDevice
from multiprocessing import Value, Process

from gpiozero import Motor, DistanceSensor  # this library uses BCM numbering
import RPi.GPIO as GPIO

import sys
import os
from time import gmtime, strftime, sleep

import csv

import numpy as np


# This function maps the gamepad joystick's control values to a point in the region [0,1] X [0,1] in R^2
def map_to_unit_interval(x, y):
    # The equation for the conversion of a single value k in the integer interval [0..255] to the real interval [0, 1] is f(k) = ((k-128)^2 / 128^2)
    # The k value 0 is given when the gamepad's joystick is totally upwards in the y axis and totally to the right in the x axis 
    Px = ((float(x)-128.0)*(float(x)-128.0))/(128.0*128.0)
    Py = ((float(y)-128.0)*(float(y)-128.0))/(128.0*128.0)
    
    # It returns a 2D numpy array with the converted values
    return np.array([Px, Py])


# Simple function to be certain that the max value is the max valid one, in this case 1
def round_to_1_if_greater(x):
    if(x > 1):
            return 1
    return x


# This function is going to be executed in a separate thread, it makes and stores the distance measurements of the ultrasonic sensors
def thread_log(pwm, pwmLeft, pwmRight, trimFactorLeft, trimFactorRight, Lx, Ly):
    # Initialize the log file's name
    scriptBasename = os.path.basename(sys.argv[0])
    logDate = strftime("_teste_%Y-%m-%d_%H:%M:%S_log.csv", gmtime())
    logfileName = scriptBasename + logDate

    # Instantiate the sensor's objects
    frontSensor = DistanceSensor(echo=23, trigger=24, max_distance=3)
    leftSensor = DistanceSensor(echo=25, trigger=8, max_distance=3)
    rightSensor = DistanceSensor(echo=17, trigger=27, max_distance=3)

    log = ["gamepadLx", "gamepadLy", "frontSensor", "rightSensor", "leftSensor", "pwm", "pwmLeft", "pwmRight"]
    with open(logfileName, 'ab') as arquivo:
        logger = csv.writer(arquivo)
        logger.writerow(log)

    # Main loop
    while(True):
        log = [float(Lx.value), float(Ly.value), (frontSensor.distance*100), (rightSensor.distance*100), (leftSensor.distance*100), pwm.value, (pwmLeft.value * (1 - trimFactorLeft.value)), (pwmRight.value * (1 - trimFactorRight.value))]
        print(log)

        with open(logfileName, 'ab') as arquivo:
            logger = csv.writer(arquivo)
            logger.writerow(log)

        sleep(0.0625)


# This function is called whenever the optic sensors detect a change in one of the wheels
def pin_changed(ticks):
    print(ticks.value)
    ticks.value = ticks.value + 1


# ...
def thread_motors_controller(ticksRight, ticksLeft, trimFactorRight, trimFactorLeft, pwmRight, pwmLeft, Lx, Ly):
    # Instantiate motors
    leftMotor = Motor(6, 5)
    rightMotor = Motor(26, 13)

    # Main loop
    while True:
        # Calculating trim factor from the encoders
        if(pwmRight.value == pwmLeft.value):
            if(ticksRight.value > ticksLeft.value):
                trimFactorRight.value = round_to_1_if_greater(trimFactorRight.value + (pwmRight.value/320)) #0.001953125    
                
            elif(ticksRight.value < ticksLeft.value):
                trimFactorLeft.value = round_to_1_if_greater(trimFactorLeft.value + (pwmLeft.value/320))
                                    
        elif(pwmRight.value > pwmLeft.value and ticksRight.value < ticksLeft.value):
            trimFactorLeft.value = round_to_1_if_greater(trimFactorLeft.value + (pwmLeft.value/320))
                
        elif(pwmRight.value < pwmLeft.value and ticksRight.value > ticksLeft.value):
            trimFactorRight.value = round_to_1_if_greater(trimFactorRight.value + (pwmRight.value/320))
        
        # Updating pwm 
        if(Ly.value < 128):
            leftMotor.stop()
            rightMotor.stop()
                
            leftMotor.forward(abs(pwmLeft.value * (1 - trimFactorLeft.value)))
            rightMotor.forward(abs(pwmRight.value * (1 - trimFactorRight.value)))

        elif(Ly.value > 128):
            leftMotor.stop()
            rightMotor.stop()
                
            leftMotor.backward(abs(pwmLeft.value * (1 - trimFactorLeft.value)))
            rightMotor.backward(abs(pwmRight.value * (1 - trimFactorRight.value)))

        elif(Ly.value == 128):
            if(Lx.value < 128):
                leftMotor.stop()
                rightMotor.stop()
                
                leftMotor.backward(abs(pwmLeft.value * (1 - trimFactorLeft.value)))
                rightMotor.forward(abs(pwmRight.value * (1 - trimFactorRight.value)))

            elif(Lx.value > 128):
                leftMotor.stop()
                rightMotor.stop()
                
                leftMotor.forward(abs(pwmLeft.value * (1 - trimFactorLeft.value)))
                rightMotor.backward(abs(pwmRight.value * (1 - trimFactorRight.value)))

            elif(Lx.value == 128):
                leftMotor.stop()
                rightMotor.stop()

        #ticksRight.value = 0    
        #ticksLeft.value = 0
        
        sleep(0.003125)


# This function calculates the amount of the PWM that have to be discounted in order for the prototipe to turn sideways
def calculate_steering_discount(pwmPoint):
    # This amount is calculated through the angle that the vector returned by the function map_to_unit_interval makes with the x axis 
    return (((1.6/np.pi)*(np.arctan2(pwmPoint[1], pwmPoint[0]))))


# This function sets the PWM values of each separate motor, using the control point generated by the gamepad  and the map_to_unit_intervalfunction
def set_pwm_value(Lx, Ly, pwmPoint, pwm, pwmLeft, pwmRight, trimFactorRight, trimFactorLeft, ticksRight, ticksLeft):
    if(Lx.value < 128):
        pwmLeft.value = abs(pwm.value - calculate_steering_discount(pwmPoint))
        pwmRight.value = abs(pwm.value)

    elif(Lx.value > 128):
        pwmLeft.value = abs(pwm.value)
        pwmRight.value = abs(pwm.value - calculate_steering_discount(pwmPoint))
        
    elif(Lx.value == 128):
        if(Ly.value != 128):
            pwmLeft.value = abs(pwm.value)
            pwmRight.value = abs(pwm.value)
        else:
            pwmLeft.value = 0
            pwmRight.value = 0
    
    trimFactorRight.value = 0
    trimFactorLeft.value = 0
    
    ticksRight.value = 0
    ticksLeft.value = 0


# This function sets the PWM values of each separate motor, using the control point generated by the gamepad  and the map_to_unit_intervalfunction
def thread_reset_factors(trimFactorRight, trimFactorLeft):
    while True:
        trimFactorRight.value = 0
        trimFactorLeft.value = 0
        
        sleep(0.8)

def thread_reset_ticks(ticksRight, ticksLeft):
    while True:                
        ticksRight.value = 0    
        ticksLeft.value = 0

        sleep(8)


# Initialize the shared variables for the gamepad's control and the motors's PWM
Ly = Value('i', 128, lock=False)
Lx = Value('i', 128, lock=False)
pwm = Value('d', -1, lock=False)
pwmLeft = Value('d', 0, lock=False)
pwmRight = Value('d', 0, lock=False)

# Initialize the factors that will be used to correct the trajectory of the prototype by damping the velocity of one wheel
trimFactorRight = Value('d', 0, lock=True)
trimFactorLeft = Value('d', 0, lock=True)
 
                
# # Initialize the motor controling process
# motorsProcess = Process(target=thread_motors, args=(trimFactorRight, trimFactorLeft, pwmLeft, pwmRight, Lx, Ly))
# motorsProcess.daemon = True
# motorsProcess.start()

# Initialize the logging process
logProcess = Process(target=thread_log, args=(pwm, pwmLeft, pwmRight, trimFactorLeft, trimFactorRight, Lx, Ly))
logProcess.daemon = True
logProcess.start()
logFlag = True
btnAclean = True

# Set GPIO pins numbering, i used the same that is used in the gpiozero library
GPIO.setmode(GPIO.BCM)
    
# Set the optic sensors's input pins. They are the reason this function can calculate the wheels's rotation and correct it
GPIO.setup(2, GPIO.IN)
GPIO.setup(3, GPIO.IN)
    
# Defining and initializing the variables for counting the wheels encoder ticks
ticksRight = Value('i', 0, lock=False)
ticksLeft = Value('i', 0, lock=False)

riseRight_detect = lambda channel, arg1=ticksRight: pin_changed(arg1)
riseLeft_detect = lambda channel, arg1=ticksLeft: pin_changed(arg1)

GPIO.add_event_detect(2, GPIO.FALLING, callback=riseRight_detect, bouncetime=25)
GPIO.add_event_detect(3, GPIO.FALLING, callback=riseLeft_detect, bouncetime=25)

# # Initialize the trajectory correction process
# encodersProcess = Process(target=thread_encoders,args=(ticksRight, ticksLeft, pwmRight, pwmLeft, trimFactorRight, trimFactorLeft))
# encodersProcess.daemon = True
# encodersProcess.start()

# Motor controlling process
motorsProcess = Process(target=thread_motors_controller, args=(ticksRight, ticksLeft, trimFactorRight, trimFactorLeft, pwmRight, pwmLeft, Lx, Ly))
motorsProcess.daemon = True
motorsProcess.start()

# ...
resetFactorsProcess = Process(target=thread_reset_factors, args=(trimFactorRight, trimFactorLeft))
resetFactorsProcess.daemon = True
resetFactorsProcess.start()

resetTicksProcess = Process(target=thread_reset_ticks, args=(ticksRight, ticksLeft))
resetTicksProcess.daemon = True
resetTicksProcess.start()


# Initialize the gamepad
gamepad = InputDevice('/dev/input/event3')
commands = {(3, 1): 'Ly', (3, 0): 'Lx', (3, 5): 'Ry', (3, 2): 'Rx', (1, 308): 'btn_Y', (1, 307): 'btn_X', (1, 304): 'btn_A', (1, 305): 'btn_B', (1, 310): 'btn_LB', (1, 311): 'btn_RB', (3, 9): 'Rt', (3, 10): 'Lt'}  # accesso: commands[(event.type,event.code)]

print("Awaiting commands:")
# Main loop based on pooling the gamepad
for event in gamepad.read_loop():
    print('btn_Y: Exit the program')
    print('btn_A: Stop/Start new log')
    print('btn_X: Go in a straight line (for calibration tests)')
    print('btn_B: Stops the calibration test')

    try:
        if(commands[(event.type, event.code)] == 'Ly'): # Update Ly and the general PWM value
            Ly.value = event.value
            pwmPoint = map_to_unit_interval(Lx.value, Ly.value)
            pwm.value = round_to_1_if_greater(np.linalg.norm(pwmPoint))
            # Set the PWM value for each motor
            set_pwm_value(Lx, Ly, pwmPoint, pwm, pwmLeft, pwmRight, trimFactorRight, trimFactorLeft, ticksRight, ticksLeft)

        elif(commands[(event.type, event.code)] == 'Lx'): # Update Lx and the PWM value
            Lx.value = event.value
            pwmPoint = map_to_unit_interval(Lx.value, Ly.value)
            pwm.value = round_to_1_if_greater(np.linalg.norm(pwmPoint))
            # Set the PWM value for each motor
            set_pwm_value(Lx, Ly, pwmPoint, pwm, pwmLeft, pwmRight, trimFactorRight, trimFactorLeft, ticksRight, ticksLeft)

        elif(commands[(event.type, event.code)] == 'btn_Y'): # Exit the program
            # Terminate log process if active 
            if(logFlag):
                logProcess.terminate()
            # Stop the motors and terminate the motors process by simulating a command on the gamepad
            Lx.value = 128
            Ly.value = 128
            set_pwm_value(Lx, Ly, pwmPoint, pwm, pwmLeft, pwmRight, trimFactorRight, trimFactorLeft, ticksRight, ticksLeft)
            motorsProcess.terminate()
            # Stop trajectory correction process and remove events from the optic sensors's pins
            # encodersProcess.terminate()
            GPIO.remove_event_detect(2)
            GPIO.remove_event_detect(3)

            resetFactorsProcess.terminate()
            resetTicksProcess.terminate()
        
            # Issue the sys command to exit
            sys.exit()

        elif(commands[(event.type, event.code)] == 'btn_A'): # Stop/Start new log
            if(btnAclean):
                if(logFlag):
                    logProcess.terminate()
                    logFlag = False
                else:
                    logProcess = Process(target=thread_log, args=(pwm, pwmLeft, pwmRight, trimFactorLeft, trimFactorRight, Lx, Ly))
                    logProcess.daemon = True
                    logProcess.start()
                    logFlag = True
                btnAclean = False
            else:
                btnAclean = True
        
        elif(commands[(event.type, event.code)] == 'btn_X'): # Go in a straight line (for calibration tests)
            # Simulates the joystick position that tells the prototype to go straight forward
            Ly.value = 0
            Lx.value = 128
            pwmPoint = map_to_unit_interval(Lx.value, Ly.value)
            pwm.value = round_to_1_if_greater(np.linalg.norm(pwmPoint))
            # Set the PWM value for each motor
            set_pwm_value(Lx, Ly, pwmPoint, pwm, pwmLeft, pwmRight, trimFactorRight, trimFactorLeft, ticksRight, ticksLeft)            
            for subEvent in gamepad.read_loop(): # Inside loop that waits for the command to stop the calibration    
                try:
                    if(commands[(subEvent.type, subEvent.code)] == 'btn_B'): # Stops the prototype and returns to the outer loop
                        Lx.value = 128
                        Ly.value = 128
                        set_pwm_value(Lx, Ly, pwmPoint, pwm, pwmLeft, pwmRight, trimFactorRight, trimFactorLeft, ticksRight, ticksLeft)
                        break
                except KeyError: # Keeps going forward otherwise
                    pass

    except KeyError:
        pass
