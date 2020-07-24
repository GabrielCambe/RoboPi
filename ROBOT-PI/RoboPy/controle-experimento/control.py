#!/usr/bin/python
from evdev import InputDevice
from multiprocessing import Value, Process
import RPi.GPIO as GPIO
import sys
import numpy as np
from ctypes import c_bool, c_char_p
import time
from os.path import basename
from datetime import datetime
from pytz import timezone
import argparse


import mathematics #from mathematics import map_to_unit_interval, round_to_1_if_greater
import motorcontrol #from motorcontrol import reset_factors, ticks_pin_changed, reset_ticks, set_pwm_value, motors_controller
import distancelog #from distancelog import thread_log
import regressor


pwmLeftA = 0.0
pwmLeftB = 1.0
pwmRightA = 0.0
pwmRightB = 1.0
#pwmLeftA, pwmLeftB, pwmRightA, pwmRightB = motors.calibrate()

ln25 = np.log(25.0)
lg11 = (np.log(11.0)/np.log(2))

WHEEL_DIAMETER_CM = 22.0
SPACES_PER_REVOLUTION = 20.0
WHEEL_AXIS_SIZE_CM = 13.0

def handle_axis_event(var, verbosity):
    pwmPoint = mathematics.map_to_unit_interval(var['Lx'].value, var['Ly'].value)
    if(not var['UsingPwmRegressor'].value):
        aux = mathematics.round_to_1_if_greater(np.linalg.norm(pwmPoint))
       
        if(aux <= 0.04):
            var['pwm'].value = 0.0
        elif(aux > 0.04 and aux <= 0.1449):
            var['pwm'].value = 1.0 + (np.log(aux)/ln25)
        elif(aux > 0.1449 and aux < 0.8526):
            var['pwm'].value = 0.2826456 * aux + 0.3590164
        elif(aux >= 0.8526):
            var['pwm'].value = np.exp(((aux - 1.0) * lg11))

    var['steerRight'].value = mathematics.calculate_steering_discount(pwmPoint)
    var['steerLeft'].value = mathematics.calculate_steering_discount(pwmPoint)

    #motorcontrol.reset_ticks(1.0, var['ticksRight'], var['ticksLeft'], False)
    if(var['Lx'].value == 128 and var['Ly'].value == 128):
        motorcontrol.reset_factors(
            1.0, var['trimFactorRight'], var['trimFactorLeft'], False
        )
                 
    motorcontrol.set_pwm_value(
        var,
        pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
        verbosity
    )


def go_forward(var, cm, verbosity):
    initial_ticksRight = var['ticksRight'].value
    initial_ticksLeft = var['ticksLeft'].value
    
    ticks = int(cm * (SPACES_PER_REVOLUTION/WHEEL_DIAMETER_CM))
    
    while ((var['ticksRight'].value - initial_ticksRight) < ticks) and ((var['ticksLeft'].value - initial_ticksLeft) < ticks):
        var['Lx'].value = 128
        var['Ly'].value = 0
        handle_axis_event(var, verbosity)
    
    print("go foward " + str(var['ticksRight'].value))
    print("go foward " + str(var['ticksLeft'].value))

    var['Ly'].value = 128
    var['Lx'].value = 128
                
    motorcontrol.reset_factors(1.0, var['trimFactorRight'], var['trimFactorLeft'], False)
    motorcontrol.reset_ticks(1.0, var['ticksRight'], var['ticksLeft'], False)
                
    # Set the PWM value for each motor
    motorcontrol.set_pwm_value(
        var,
        pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
        var
    )


def go_right(var, deg, verbosity): 
    arcLenght_cm = (deg/360.0) * (2 * np.math.pi * (WHEEL_DIAMETER_CM/2.0))
    ticks = int(arcLenght_cm * (SPACES_PER_REVOLUTION/WHEEL_DIAMETER_CM))
    
    initial_ticksRight = var['ticksRight'].value

    while (var['ticksRight'].value - initial_ticksRight) < ticks:
        var['Lx'].value = 255
        var['Ly'].value = 128
        handle_axis_event(var, verbosity)
    
    print("go_right " + str(var['ticksRight'].value))

    var['Ly'].value = 128
    var['Lx'].value = 128
                
    motorcontrol.reset_factors(1.0, var['trimFactorRight'], var['trimFactorLeft'], False)
    motorcontrol.reset_ticks(1.0, var['ticksRight'], var['ticksLeft'], False)
                
    # Set the PWM value for each motor
    motorcontrol.set_pwm_value(
        var,
        pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
        var
    )


def go_left(var, deg, verbosity): 
    arcLenght_cm = (deg/360.0) * (2 * np.math.pi * (WHEEL_DIAMETER_CM/2.0))
    ticks = int(arcLenght_cm * (SPACES_PER_REVOLUTION/WHEEL_DIAMETER_CM))
    
    initial_ticksLeft = var['ticksLeft'].value

    while (var['ticksLeft'].value - initial_ticksLeft) < ticks:
        var['Lx'].value = 0
        var['Ly'].value = 128
        handle_axis_event(var, verbosity)
    
    print("go_left " + str(var['ticksLeft'].value))

    var['Ly'].value = 128
    var['Lx'].value = 128
                
    motorcontrol.reset_factors(1.0, var['trimFactorRight'], var['trimFactorLeft'], False)
    motorcontrol.reset_ticks(1.0, var['ticksRight'], var['ticksLeft'], False)
                
    # Set the PWM value for each motor
    motorcontrol.set_pwm_value(
        var,
        pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
        var
    )


parser = argparse.ArgumentParser()
parser.add_argument( "-r", "--regressor",
    dest='regressor',
    type=str, nargs='?',
    action='store',
    required=False,
    const=None, default=None,
    help="Path to a regressor's pickle dump to be loaded to the program\s CONTROL regressor."
)
parser.add_argument( "-v", "--verbosity",
    type=str, nargs='+', choices=['log', 'commands', 'logic', 'motor', 'encoder'],
    dest='verbosity',
    action='store',
    const=None, default=None,
    help="Print verbose information",
)
args = parser.parse_args()


var = {
    'Ly': Value('i', 128, lock=False),
    'Lx': Value('i', 128, lock=False),
    'pwm': Value('d', -1.0, lock=False),
    'pwmLeft': Value('d', 0.0, lock=False),
    'pwmRight': Value('d', 0.0, lock=False),
    'trimFactorRight': Value('d', 0.0, lock=True),
    'trimFactorLeft': Value('d', 0.0, lock=True),
    'distF': Value('d', 0.0, lock=False),
    'distR': Value('d', 0.0, lock=False),
    'distL': Value('d', 0.0, lock=False),
    'steerLeft': Value('d', 0.0, lock=False),
    'steerRight': Value('d', 0.0, lock=False),
    'ticksRight': Value('i', 0, lock=False),
    'ticksLeft': Value('i', 0, lock=False),
    'ticksRightDirection': Value('i', 0, lock=False),
    'ticksLeftDirection': Value('i', 0, lock=False),
    'UsingPwmRegressor': Value(c_bool, False, lock=False),
    'PwmRegressorLoaded': Value(c_bool, False, lock=False),
    'time': Value('d', 0.0, lock=False),
    'UsingRegressor': Value(c_bool, False, lock=False),
    'RegressorLoaded': Value(c_bool, False, lock=False),
    'UsingLogic': Value(c_bool, False, lock=False)
}


# Set GPIO pins numbering, i used the same that is used in the gpiozero library
GPIO.setmode(GPIO.BCM)
# Set the optic sensors's input pins. They are the reason this function can calculate the wheels's rotation and correct it
GPIO.setup(2, GPIO.IN)
GPIO.setup(3, GPIO.IN)


logProcess = Process(
    target=distancelog.thread_log,
    args=(
        256.0,
        var,
        args.verbosity
    )
)
logProcess.daemon = True
logProcess.start()
logFlag = True

# Motor controlling process
motorsProcess = Process(
    target=motorcontrol.motors_controller,
    args=(
        512.0,
        var,
        pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
        args.verbosity
    )
)
motorsProcess.daemon = True
motorsProcess.start()

# Creating the callback functions for the optic encoder interrupts
riseRight_detect = lambda channel,arg1=(var['ticksRight']): motorcontrol.encoder_pin_callback(arg1)
riseLeft_detect = lambda channel, arg1=(var['ticksLeft']): motorcontrol.encoder_pin_callback(arg1)

GPIO.add_event_detect(2, GPIO.BOTH, callback=riseRight_detect, bouncetime=10)
GPIO.add_event_detect(3, GPIO.BOTH, callback=riseLeft_detect, bouncetime=10)


# Load the regressor passed as an argument
if args.regressor:
    try:
        controlRegressor = regressor.loadRegressor(args.regressor)
        var['UsingRegressor'].value = False
        var['RegressorLoaded'].value = True
    except (NameError, IOError) as error:
        print(error)
        var['UsingRegressor'].value = False
        var['RegressorLoaded'].value = False
else:
    print("Regressor Not loaded!")
    var['UsingRegressor'].value = False
    var['RegressorLoaded'].value = False


# Initialize the gamepad
gamepad = InputDevice('/dev/input/event3')
# accesso: commands[(event.type,event.code)]
commands = {
    (3, 1): 'Ly',
    (3, 0): 'Lx', 
    (3, 5): 'Ry', 
    (3, 2): 'Rx',
    (1, 308): 'btn_Y',
    (1, 307): 'btn_X', 
    (1, 304): 'btn_A',
    (1, 305): 'btn_B',
    (1, 310): 'btn_LB',
    (1, 311): 'btn_RB',
    (3, 9): 'Rt',
    (3, 10): 'Lt',
    (0,0): 'sync'
}


print("Awaiting commands:")
print('btn_Y: Exit the program')
print('btn_A: Stop/Start new log')
print('btn_LB: Go in a straight line (for calibration tests)')
print('btn_RB: Stops the calibration test and returns to the outer loop')

while True:
    event = gamepad.read_one()
    if args.verbosity:
        if 'commands' in args.verbosity:
            try:
                print("Command: " + str(commands[(event.type, event.code)]))
                print("Value: " + str(event.value))
            except (AttributeError, KeyError) as error:
                pass

        if 'encoder' in args.verbosity:
            print("ticksLeft: " + str(var['ticksLeft'].value))
            print("ticksRight: " + str(var['ticksRight'].value))


    if (var['UsingRegressor'].value):
        features = np.asarray(
            [[
                var['distF'].value, var['distR'].value, var['distL'].value,
                var['ticksRight'].value, var['ticksLeft'].value
            ]],
            dtype=float
        )
        prediction = controlRegressor.predict(features)        
        var['Lx'].value = int(prediction[0][0]) 
        var['Ly'].value = int(prediction[0][1])
        
        handle_axis_event(var, args.verbosity)

    elif (var['UsingLogic'].value):
        # go_forward(var, 25.0, args.verbosity) 
        # go_left(var, 90.0, args.verbosity)
        # go_right(var, 90.0, args.verbosity)

        # if(var['UsingLogic'].value == True):
        #     var['UsingLogic'].value = False
        # else:
        #     var['UsingLogic'].value = True
        #     var['UsingRegressor'].value = False


        # if var['distF'].value > 25.0:
        #     var['Ly'].value = 0
        #     if (var['distL'].value - ((var['distL'].value + var['distR'].value)/2.0)) > 5.0:
        #         var['Lx'].value = np.clip(var['Lx'].value - 4, 0, 255)
        #     elif (var['distR'].value - ((var['distL'].value + var['distR'].value)/2.0)) > 5.0:
        #         var['Lx'].value = np.clip(var['Lx'].value + 4, 0, 255)
        # else:
        #     var['Lx'].value = 128
        #     var['Ly'].value = 128

        
        if var['distF'].value > 25.0:
            go_forward(var, 25.0, args.verbosity) 
        else:
            var['Lx'].value = 128
            var['Ly'].value = 128
            
        if var['distL'].value >= var['distR'].value:
            go_left(var, 90.0, args.verbosity)
        else:
            go_right(var, 90.0, args.verbosity)

        if args.verbosity:
            if ('logic' in args.verbosity):
                print("Lx: " + str(var['Lx'].value) + ", Ly: " + str(var['Ly'].value))

        time.sleep(1.0/4.0)

    try: 
        if(commands[(event.type, event.code)] == 'Ly' and (not var['UsingRegressor'].value) and (not var['UsingLogic'].value)): # Update Ly and the general PWM value
            var['Ly'].value = event.value
            handle_axis_event(var, args.verbosity)


        elif(commands[(event.type, event.code)] == 'Lx' and (not var['UsingRegressor'].value) and (not var['UsingLogic'].value)): # Update Lx and the PWM value
            var['Lx'].value = event.value
            handle_axis_event(var, args.verbosity)
                    

        elif(commands[(event.type, event.code)] == 'btn_LB'): # Go in a straight line (for calibration tests)
            if(event.value == 1): # The key was pressed, not released
                # Simulates the joystick position that tells the prototype to go straight forward
                var['Ly'].value = 0
                var['Lx'].value = 128
                pwmPoint = mathematics.map_to_unit_interval(var['Lx'].value, var['Ly'].value)
                var['pwm'].value = 0.0
                
                motorcontrol.reset_factors(1.0, var['trimFactorRight'], var['trimFactorLeft'], False)
                motorcontrol.reset_ticks(1.0, var['ticksRight'], var['ticksLeft'], False)
                
                # Set the PWM value for each motor
                motorcontrol.set_pwm_value(
                    var,
                    pwmLeftA, pwmLeftB, pwmRightA, pwmRightB
                )

                for subEvent in gamepad.read_loop(): # Inside loop that waits for the command to stop the calibration    
                    try:
                        if(commands[(subEvent.type, subEvent.code)] == 'Rt'): # Define PWM
                            var['pwm'].value = float(subEvent.value)/255.0

                            #motorcontrol.reset_factors(1.0, trimFactorRight, trimFactorLeft, False)
                            motorcontrol.reset_ticks(
                                1.0, var['ticksRight'], var['ticksLeft'], False
                            )
                            # Set the PWM value for each motor
                            motorcontrol.set_pwm_value(
                                var,
                                pwmLeftA, pwmLeftB, pwmRightA, pwmRightB
                            )


                        elif(commands[(subEvent.type, subEvent.code)] == 'btn_RB'): # Stops the calibration test and returns to the outer loop
                            var['Lx'].value = 128
                            var['Ly'].value = 128
                            pwmPoint = mathematics.map_to_unit_interval(var['Lx'].value, var['Ly'].value)
                            var['pwm'].value = 0.0

                            motorcontrol.reset_factors(1.0, var['trimFactorRight'], var['trimFactorLeft'], False)
                            motorcontrol.reset_ticks(1.0, var['ticksRight'], var['ticksLeft'], False)
                            # Set the PWM value for each motor
                            motorcontrol.set_pwm_value(
                                var,
                                pwmLeftA, pwmLeftB, pwmRightA, pwmRightB
                            )
                            
                            break
                        
                    except KeyError: # Keeps going forward otherwise
                        pass


        elif(commands[(event.type, event.code)] == 'btn_B'): # Go in a straight line (for calibration tests)
            if(event.value == 1): # The key was pressed, not released
                # Simulates the joystick position that tells the prototype to go straight forward
                var['Ly'].value = 128
                var['Lx'].value = 128
                
                motorcontrol.reset_factors(1.0, var['trimFactorRight'], var['trimFactorLeft'], False)
                motorcontrol.reset_ticks(1.0, var['ticksRight'], var['ticksLeft'], False)
                
                # Set the PWM value for each motor
                motorcontrol.set_pwm_value(
                    var,
                    pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                    var
                )

                if(var['UsingLogic'].value == True):
                    var['UsingLogic'].value = False
                else:
                    var['UsingLogic'].value = True
                    var['UsingRegressor'].value = False


        elif(commands[(event.type, event.code)] == 'btn_A'): # Stop/Start new log
            if(event.value == 1): # The key was pressed, not released
                if(logFlag):
                    logProcess.terminate()
                    del logProcess
                    logFlag = False
                    logProcess = Process(
                        target=distancelog.thread_log,
                        args=(
                            256.0,
                            var,
                            True
                        )
                    )
                else:
                    logProcess.daemon = True
                    logProcess.start()
                    logFlag = True


        elif(commands[(event.type, event.code)] == 'btn_X'): # Stop/Start regression
            if(event.value == 1): # The key was pressed, not released
                if(var['RegressorLoaded'].value and var['UsingRegressor'].value):
                    print("\n\nRegressor OFF!\n\n")
                    var['UsingRegressor'].value = False
                else:
                    if(var['RegressorLoaded'].value):
                        print("\n\nRegressor ON!\n\n")
                        var['UsingRegressor'].value = True
                        var['UsingLogic'].value = False
                    else:
                        print('\n\nRegressor Not Loaded!\n\n')


        elif(commands[(event.type, event.code)] == 'btn_Y'): # Exit the program
            # Terminate log process if active 
            if(logFlag):
                logProcess.terminate()
            # Stop the motors and terminate the motors process by simulating a command on the gamepad
            var['Lx'].value = 128
            var['Ly'].value = 128
            pwmPoint = mathematics.map_to_unit_interval(var['Lx'].value, var['Ly'].value)
            var['pwm'].value = 0.0
            
            motorcontrol.set_pwm_value(
                var,
                pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                args.verbosity
            )
            motorsProcess.terminate()
            
            # Remove events from the optic sensors's pins
            GPIO.remove_event_detect(2)
            GPIO.remove_event_detect(3)
                    
            # Exit program
            sys.exit()
            
    except (KeyError, AttributeError) as error:
        pass