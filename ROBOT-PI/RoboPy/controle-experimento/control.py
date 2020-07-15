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


import mathematics #from mathematics import map_to_unit_interval, round_to_1_if_greater
import motorcontrol #from motorcontrol import reset_factors, ticks_pin_changed, reset_ticks, set_pwm_value, motors_controller
import distancelog #from distancelog import thread_log
import regressor

# Initialize the shared variables for the gamepad's control and the motors's PWM
Ly = Value('i', 128, lock=False)
Lx = Value('i', 128, lock=False)
pwm = Value('d', -1.0, lock=False)
pwmLeft = Value('d', 0.0, lock=False)
pwmRight = Value('d', 0.0, lock=False)
pwmLeftA = 0.0
pwmLeftB = 1.0
pwmRightA = 0.0
pwmRightB = 1.0
#pwmLeftA, pwmLeftB, pwmRightA, pwmRightB = motors.calibrate()
        

# Initialize the factors that will be used to correct the trajectory of the prototype by damping the velocity of the wheels
trimFactorRight = Value('d', 0.0, lock=True)
trimFactorLeft = Value('d', 0.0, lock=True)

# Initialize the shared variables that will store the distance measurements
distF = Value('d', 0.0, lock=False)
distR = Value('d', 0.0, lock=False)
distL = Value('d', 0.0, lock=False)


# Initialize the varoables from the steer process
steerFlag = Value(c_bool, False, lock=False)
direction = 0
steerLeft = Value('d', 0.0, lock=False)
steerRight = Value('d', 0.0, lock=False)
usingSteerRegressor = Value(c_bool, False, lock=False)
steerRegressorLoaded = Value(c_bool, False, lock=False)


# Set GPIO pins numbering, i used the same that is used in the gpiozero library
GPIO.setmode(GPIO.BCM)
# Set the optic sensors's input pins. They are the reason this function can calculate the wheels's rotation and correct it
GPIO.setup(2, GPIO.IN)
GPIO.setup(3, GPIO.IN)
    
# Defining and initializing the variables for counting the wheels encoder ticks
ticksRight = Value('i', 0, lock=False)
ticksLeft = Value('i', 0, lock=False)


# Create boolean variable to control the regressor usage
UsingPwmRegressor = Value(c_bool, False, lock=False)
PwmRegressorLoaded = Value(c_bool, False, lock=False)


seconds = Value('d', 0.0, lock=False)

logProcess = Process(
                target=distancelog.thread_log,
                args=(
                    256.0,
                    pwm, pwmLeft, pwmRight,
                    trimFactorLeft, trimFactorRight,
                    Lx, Ly,
                    distF, distR, distL,
                    steerLeft, steerRight,
                    ticksLeft, ticksRight,
                    seconds,
                    True
                ))
logProcess.daemon = True
logProcess.start()
logFlag = True


# Motor controlling process
try:
    motorsProcess = Process(
                        target=motorcontrol.motors_controller,
                        args=(
                            512.0,
                            ticksRight, ticksLeft,
                            trimFactorRight, trimFactorLeft,
                            pwm, pwmRight, pwmLeft,
                            Lx, Ly,
                            sys.argv[1], UsingPwmRegressor, PwmRegressorLoaded,
                            distF, distR, distL,
                            pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                            steerLeft, steerRight, steerFlag,
                            seconds))
    motorsProcess.daemon = True
    motorsProcess.start()

except (IndexError, IOError) as error:
    print(error)
    motorsProcess = Process(
                        target=motorcontrol.motors_controller,
                        args=(
                            512.0,
                            ticksRight, ticksLeft,
                            trimFactorRight, trimFactorLeft,
                            pwm, pwmRight, pwmLeft,
                            Lx, Ly,
                            "", UsingPwmRegressor, PwmRegressorLoaded,
                            distF, distR, distL,
                            pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                            steerLeft, steerRight, steerFlag,
                            seconds))
    motorsProcess.daemon = True
    motorsProcess.start()

# Creating the callback functions for the optic encoder interrupts
riseRight_detect = lambda channel,arg1=(
                                    ticksRight,
                                    pwmRight, pwmLeft,
                                    ticksRight, ticksLeft,
                                    trimFactorRight, trimFactorLeft,
                                    512.0,
                                    UsingPwmRegressor
                                    ): motorcontrol.encoder_pin_callback(arg1)

riseLeft_detect = lambda channel, arg1=(
                                    ticksLeft,
                                    pwmRight, pwmLeft,
                                    ticksRight, ticksLeft,
                                    trimFactorRight, trimFactorLeft,
                                    512.0,
                                    UsingPwmRegressor
                                    ): motorcontrol.encoder_pin_callback(arg1)

GPIO.add_event_detect(2, GPIO.BOTH, callback=riseRight_detect, bouncetime=25)
GPIO.add_event_detect(3, GPIO.BOTH, callback=riseLeft_detect, bouncetime=25)


# Create boolean variable to control the regressor usage
UsingRegressor = Value(c_bool, False, lock=False)
RegressorLoaded = Value(c_bool, False, lock=False)

try:
    # Load the regressor passed as an argument
    if(sys.argv[1]):
        try:
            controlRegressor = regressor.loadRegressor(sys.argv[1])
            UsingRegressor.value = False
            RegressorLoaded.value = True
        except (NameError, IOError) as error:
            print(error)
            UsingRegressor.value = False
            RegressorLoaded.value = False
    else:
        print("Regressor Not loaded!")
        UsingRegressor.value = False
        RegressorLoaded.value = False
except (IndexError, IOError) as error:
    pass


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

ln25 = np.log(25.0)
lg11 = (np.log(11.0)/np.log(2))

while(True):
    event = gamepad.read_one()
# Main loop based on pooling the gamepad
# for event in gamepad.read_loop():
    try: 
        if (UsingRegressor.value):
            features = np.asarray([[distF.value, distR.value, distL.value, steerLeft.value, steerRight.value]], dtype=float)
            prediction = controlRegressor.predict(features)        
            Lx.value = int(prediction[0][0])
            Ly.value = int(prediction[0][1])
            print("Lx: " + str(prediction[0][0]) + ", Ly: " + str(prediction[0][1]))
            
            pwmPoint = mathematics.map_to_unit_interval(Lx.value, Ly.value)
            if(not UsingPwmRegressor.value):
                aux = mathematics.round_to_1_if_greater(np.linalg.norm(pwmPoint))
               
                if(aux <= 0.04):
                    pwm.value = 0.0
                elif(aux > 0.04 and aux <= 0.1449):
                    pwm.value = 1.0 + (np.log(aux)/ln25)
                elif(aux > 0.1449 and aux < 0.8526):
                    pwm.value = 0.2826456 * aux + 0.3590164
                elif(aux >= 0.8526):
                    pwm.value = np.exp(((aux - 1.0) * lg11))

                # corredorMaior = 120.0
                # pwm.value = mathematics.round_to_1_if_greater((distR.value + distL.value)/corredorMaior)

            if(not steerFlag.value):
                steerRight.value = mathematics.calculate_steering_discount(pwmPoint)
                steerLeft.value = mathematics.calculate_steering_discount(pwmPoint)

            motorcontrol.reset_ticks(1.0, ticksRight, ticksLeft, False)
            if(Lx.value == 128 and Ly.value == 128):
                motorcontrol.reset_factors(1.0, trimFactorRight, trimFactorLeft, False)
                 
            motorcontrol.set_pwm_value(
                                        Lx, Ly,
                                        pwmPoint, pwm, pwmLeft, pwmRight,
                                        UsingPwmRegressor,
                                        pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                                        steerLeft, steerRight, steerFlag
                                    )


        if(commands[(event.type, event.code)] == 'Ly' and (not UsingRegressor.value)): # Update Ly and the general PWM value
            Ly.value = event.value
            pwmPoint = mathematics.map_to_unit_interval(Lx.value, Ly.value)
            if(not UsingPwmRegressor.value):
                aux = mathematics.round_to_1_if_greater(np.linalg.norm(pwmPoint))
               
                if(aux <= 0.04):
                    pwm.value = 0.0
                elif(aux > 0.04 and aux <= 0.1449):
                    pwm.value = 1.0 + (np.log(aux)/ln25)
                elif(aux > 0.1449 and aux < 0.8526):
                    pwm.value = 0.2826456 * aux + 0.3590164
                elif(aux >= 0.8526):
                    pwm.value = np.exp(((aux - 1.0) * lg11))

                # corredorMaior = 120.0
                # pwm.value = mathematics.round_to_1_if_greater((distR.value + distL.value)/corredorMaior)

            if(not steerFlag.value):
                steerRight.value = mathematics.calculate_steering_discount(pwmPoint)
                steerLeft.value = mathematics.calculate_steering_discount(pwmPoint)

            motorcontrol.reset_ticks(1.0, ticksRight, ticksLeft, False)
            if(Lx.value == 128 and Ly.value == 128):
                motorcontrol.reset_factors(1.0, trimFactorRight, trimFactorLeft, False)
                 
            motorcontrol.set_pwm_value(
                                        Lx, Ly,
                                        pwmPoint, pwm, pwmLeft, pwmRight,
                                        UsingPwmRegressor,
                                        pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                                        steerLeft, steerRight, steerFlag
                                    )

            
        elif(commands[(event.type, event.code)] == 'Lx' and (not UsingRegressor.value)): # Update Lx and the PWM value
            Lx.value = event.value
            pwmPoint = mathematics.map_to_unit_interval(Lx.value, Ly.value)
            if(not UsingPwmRegressor.value):
                aux = mathematics.round_to_1_if_greater(np.linalg.norm(pwmPoint))
                
                if(aux <= 0.04):
                    pwm.value = 0.0
                elif(aux > 0.04 and aux <= 0.1449):
                    pwm.value = 1.0 + (np.log(aux)/ln25)
                elif(aux > 0.1449 and aux < 0.8526):
                    pwm.value = 0.2826456 * aux + 0.3590164
                elif(aux >= 0.8526):
                    pwm.value = np.exp(((aux - 1.0) * lg11))

                # corredorMaior = 120.0
                # pwm.value = mathematics.round_to_1_if_greater((distR.value + distL.value)/corredorMaior)

            if(not steerFlag.value):
                steerRight.value = mathematics.calculate_steering_discount(pwmPoint)
                steerLeft.value = mathematics.calculate_steering_discount(pwmPoint)

            motorcontrol.reset_factors(1.0, trimFactorRight, trimFactorLeft, False)
            if(Lx.value == 128 and Ly.value == 128):
                motorcontrol.reset_ticks(1.0, ticksRight, ticksLeft, False)    
                
            # Set the PWM value for each motor            
            motorcontrol.set_pwm_value(
                                        Lx, Ly,
                                        pwmPoint, pwm, pwmLeft, pwmRight,
                                        UsingPwmRegressor,
                                        pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                                        steerLeft, steerRight, steerFlag
                                    )

                    
        elif(commands[(event.type, event.code)] == 'btn_LB'): # Go in a straight line (for calibration tests)
            # Simulates the joystick position that tells the prototype to go straight forward
            Ly.value = 0
            Lx.value = 128
            pwmPoint = mathematics.map_to_unit_interval(Lx.value, Ly.value)
            pwm.value = 0.0
            
            motorcontrol.reset_factors(1.0, trimFactorRight, trimFactorLeft, False)
            motorcontrol.reset_ticks(1.0, ticksRight, ticksLeft, False)
            
            # Set the PWM value for each motor
            motorcontrol.set_pwm_value(
                                        Lx, Ly,
                                        pwmPoint, pwm, pwmLeft, pwmRight,
                                        UsingPwmRegressor,
                                        pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                                        steerLeft, steerRight, steerFlag
                                    )

            for subEvent in gamepad.read_loop(): # Inside loop that waits for the command to stop the calibration    
                try:
                    if(commands[(subEvent.type, subEvent.code)] == 'Rt'): # Define PWM
                        pwm.value = float(subEvent.value)/255.0

                        #motorcontrol.reset_factors(1.0, trimFactorRight, trimFactorLeft, False)
                        motorcontrol.reset_ticks(1.0, ticksRight, ticksLeft, False)
                        # Set the PWM value for each motor
                        motorcontrol.set_pwm_value(
                                                    Lx, Ly,
                                                    pwmPoint, pwm, pwmLeft, pwmRight,
                                                    UsingPwmRegressor,
                                                    pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                                                    steerLeft, steerRight, steerFlag
                                                )


                    elif(commands[(subEvent.type, subEvent.code)] == 'btn_RB'): # Stops the calibration test and returns to the outer loop
                        Lx.value = 128
                        Ly.value = 128
                        pwmPoint = mathematics.map_to_unit_interval(Lx.value, Ly.value)
                        pwm.value = 0.0

                        motorcontrol.reset_factors(1.0, trimFactorRight, trimFactorLeft, False)
                        motorcontrol.reset_ticks(1.0, ticksRight, ticksLeft, False)
                        # Set the PWM value for each motor
                        motorcontrol.set_pwm_value(
                                                    Lx, Ly,
                                                    pwmPoint, pwm, pwmLeft, pwmRight,
                                                    UsingPwmRegressor,
                                                    pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                                                    steerLeft, steerRight, steerFlag
                                                )
                        
                        break
                    
                except KeyError: # Keeps going forward otherwise
                    pass


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
                                                    pwm, pwmLeft, pwmRight,
                                                    trimFactorLeft, trimFactorRight,
                                                    Lx, Ly,
                                                    distF, distR, distL,
                                                    steerLeft, steerRight,
                                                    False
                                                ))
                else:
                    logProcess.daemon = True
                    logProcess.start()
                    logFlag = True


        elif(commands[(event.type, event.code)] == 'btn_X'): # Sets the flag that causes the robot to use the regrssor for the pwm values
            if(event.value == 1): # The key was pressed, not released
                if(RegressorLoaded.value and UsingRegressor.value):
                    print("\n\nRegressor OFF!\n\n")
                    UsingRegressor.value = False
                else:
                    if(RegressorLoaded.value):
                        print("\n\nRegressor ON!\n\n")
                        UsingRegressor.value = True
                    else:
                        print('\n\nRegressor Not Loaded!\n\n')


        elif(commands[(event.type, event.code)] == 'btn_B'): # Stop/Start automatic steering
            if(event.value == 1): # The key was pressed, not released
                if(steerFlag.value):
                    print("\n\nSteering OFF!\n\n")
                    steerProcess.terminate()
                    del steerProcess
                    steerFlag.value = False

                else:
                    print("\n\nSteering ON!\n\n")
                    try:
                        steerProcess = Process(
                                                target=motorcontrol.auto_steer,
                                                args=(
                                                    512.0,
                                                    direction,
                                                    pwmRight, pwmLeft,
                                                    distF, distR, distL,
                                                    steerLeft, steerRight,
                                                    sys.argv[2], usingSteerRegressor, steerRegressorLoaded))

                    except (IndexError, IOError) as error:
                        print(error)
                        steerProcess = Process(
                                            target=motorcontrol.auto_steer,
                                            args=(
                                                512.0,
                                                direction,
                                                pwmRight, pwmLeft,
                                                distF, distR, distL,
                                                steerLeft, steerRight,
                                                "", usingSteerRegressor, steerRegressorLoaded))

                    steerProcess.daemon = True
                    steerProcess.start()
                    steerFlag.value = True


        elif(commands[(event.type, event.code)] == 'btn_Y'): # Exit the program
            # Terminate log process if active 
            if(logFlag):
                logProcess.terminate()
            # Stop the motors and terminate the motors process by simulating a command on the gamepad
            Lx.value = 128
            Ly.value = 128
            pwmPoint = mathematics.map_to_unit_interval(Lx.value, Ly.value)
            pwm.value = 0.0
            
            motorcontrol.set_pwm_value(
                                        Lx, Ly,
                                        pwmPoint, pwm, pwmLeft, pwmRight,
                                        UsingPwmRegressor,
                                        pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                                        steerLeft, steerRight, steerFlag
                                    )
            motorsProcess.terminate()
            
            # Remove events from the optic sensors's pins
            GPIO.remove_event_detect(2)
            GPIO.remove_event_detect(3)
            
            # resetFactorsProcess.terminate()
            #resetTicksProcess.terminate()
        
            # Exit program
            sys.exit()
            
    
    except (KeyError, AttributeError) as error:
        pass

    #time.sleep(1.0/1000000000.0)