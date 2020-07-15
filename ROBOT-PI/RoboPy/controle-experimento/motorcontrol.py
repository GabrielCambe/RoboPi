import numpy as np
from time import sleep
from gpiozero import Motor  # this library uses BCM numbering for the Pi's pins

import mathematics #from math import calculate_steering_discount, round_to_1_if_greater
import regressor #from regressor import loadRegressor
import filters

# .o
def update_trim_factors(
                            pwmRight, pwmLeft,
                            ticksRight, ticksLeft, trimFactorRight, trimFactorLeft,
                            frequency,
                            UsingPwmRegressor
                        ):
    if(UsingPwmRegressor.value):
        # Calculating trim factor using the encoder information
        resolution = (frequency/3.0)
    else:
        resolution = frequency/2.0
    
    ticksDiff = abs(float(ticksRight.value - ticksLeft.value))
    pwmDiff = pwmRight.value - pwmLeft.value

    if(pwmDiff == 0):
        if((ticksDiff) > 0):
            trimFactorRight.value = mathematics.round_to_1_if_greater(trimFactorRight.value + (pwmRight.value/resolution))    
            trimFactorLeft.value = mathematics.round_to_0_if_smaller(trimFactorLeft.value - (pwmLeft.value/2*resolution))
            
        elif((ticksDiff) < 0):
            trimFactorRight.value = mathematics.round_to_0_if_smaller(trimFactorRight.value - (pwmRight.value/2*resolution))
            trimFactorLeft.value = mathematics.round_to_1_if_greater(trimFactorLeft.value + (pwmLeft.value/resolution))
            
    elif(pwmDiff > 0):
        if(ticksDiff <= 0):
            trimFactorRight.value = mathematics.round_to_0_if_smaller(trimFactorRight.value - (pwmRight.value/2*resolution))
            trimFactorLeft.value = mathematics.round_to_1_if_greater(trimFactorLeft.value + (pwmLeft.value/resolution))
        
        elif(ticksDiff > 0):
            trimFactorRight.value = mathematics.round_to_0_if_smaller(trimFactorRight.value - (pwmRight.value/2*resolution))
            trimFactorLeft.value = mathematics.round_to_0_if_smaller(trimFactorLeft.value - (pwmLeft.value/resolution))

    elif(pwmDiff < 0):
        if(ticksDiff >= 0):
            trimFactorRight.value = mathematics.round_to_1_if_greater(trimFactorRight.value + (pwmRight.value/resolution))    
            trimFactorLeft.value = mathematics.round_to_0_if_smaller(trimFactorLeft.value - (pwmLeft.value/2*resolution))

        elif(ticksDiff < 0):
            trimFactorRight.value = mathematics.round_to_0_if_smaller(trimFactorRight.value - (pwmRight.value/2*resolution))
            trimFactorLeft.value = mathematics.round_to_0_if_smaller(trimFactorLeft.value - (pwmLeft.value/resolution))
    
# This function sets the PWM values of each separate motor, using the control point generated by the gamepad  and the map_to_unit_intervalfunction
def reset_factors(frequency, trimFactorRight, trimFactorLeft, loop):
    if(loop):
        while True:
            trimFactorRight.value = 0
            sleep((1.0/frequency))
            
    else:
        trimFactorRight.value = 0
        trimFactorLeft.value = 0
            

# This function is called whenever the optic sensors detect a change in one of the wheels
def ticks_pin_changed(ticks):
    ticks.value = ticks.value + 1

# This function is called whenever the optic sensors detect a change in one of the wheels
def encoder_pin_callback(tuple):
    ticks, pwmRight, pwmLeft, ticksRight, ticksLeft, trimFactorRight, trimFactorLeft, frequency, UsingPwmRegressor = tuple
    #print(ticks.value)
    ticks.value = ticks.value + 1
    #update_trim_factors(pwmRight, pwmLeft, ticksRight, ticksLeft, trimFactorRight, trimFactorLeft, frequency, UsingPwmRegressor)
                
# ..                
def reset_ticks(frequency, ticksRight, ticksLeft, loop):
    if(loop):
        while True:                
            ticksRight.value = 0    
            ticksLeft.value = 0
            sleep((1.0/frequency))
    else:
        ticksRight.value = 0    
        ticksLeft.value = 0
        
        
# This function sets the PWM values of each separate motor, using the control point generated by the gamepad  and the map_to_unit_intervalfunction
def set_pwm_value(
                    Lx, Ly,
                    pwmPoint, pwm, pwmLeft, pwmRight,
                    UsingPwmRegressor, pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                    steerLeft, steerRight, steerFlag
                ):
    if(not UsingPwmRegressor.value):
        pwmLeftA = 0.0
        pwmLeftB = 1.0
        pwmRightA = 0.0
        pwmRightB = 1.0        

    if(Lx.value < 128):
        if(Ly.value != 128):
            if(steerFlag.value):    
                pwmLeft.value = (pwmLeftB - pwmLeftA) * (abs(pwm.value) - (abs(pwm.value) * steerLeft.value)) + pwmLeftA
                pwmRight.value = (pwmRightB - pwmRightA) * (abs(pwm.value) + (abs(pwm.value) * steerRight.value)) + pwmRightA
            else:
                pwmLeft.value = (pwmLeftB - pwmLeftA) * (abs(pwm.value) - (abs(pwm.value) * steerLeft.value)) + pwmLeftA
                pwmRight.value = (pwmRightB - pwmRightA) * abs(pwm.value) + pwmRightA
        else:
            pwmLeft.value = (pwmLeftB - pwmLeftA) * abs(pwm.value) + pwmLeftA
            pwmRight.value = (pwmRightB - pwmRightA) * abs(pwm.value) + pwmRightA
            
    elif(Lx.value > 128):
        if(Ly.value != 128):
            if(steerFlag.value):    
                pwmLeft.value = (pwmLeftB - pwmLeftA) * (abs(pwm.value) + (abs(pwm.value) * steerLeft.value)) + pwmLeftA
                pwmRight.value = (pwmRightB - pwmRightA) * (abs(pwm.value) - (abs(pwm.value) * steerRight.value)) + pwmRightA
            else:
                pwmLeft.value = (pwmLeftB - pwmLeftA) * abs(pwm.value) + pwmLeftA
                pwmRight.value = (pwmRightB - pwmRightA) * (abs(pwm.value) - (abs(pwm.value) * steerRight.value)) + pwmRightA
        else:
            pwmLeft.value = (pwmLeftB - pwmLeftA) * abs(pwm.value) + pwmLeftA
            pwmRight.value = (pwmRightB - pwmRightA) * abs(pwm.value) + pwmRightA
    
    elif(Lx.value == 128):
        if(Ly.value != 128):
            pwmLeft.value = (pwmLeftB - pwmLeftA) * abs(pwm.value) + pwmLeftA
            pwmRight.value = (pwmRightB - pwmRightA) * abs(pwm.value) + pwmRightA
        else:
            pwmLeft.value = 0
            pwmRight.value = 0                
                    
    
# ...
def motors_controller(
                        frequency,
                        ticksRight, ticksLeft,
                        trimFactorRight, trimFactorLeft,
                        pwm, pwmRight, pwmLeft,
                        Lx, Ly,
                        pwmRegressorPicklePath, UsingPwmRegressor, PwmRegressorLoaded,
                        distF, distR, distL,
                        pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                        steerLeft, steerRight, steerFlag,
                        seconds
                    ):
    # Load the regressor passed as an argument
    if(pwmRegressorPicklePath):
        try:
            pwmRegressor = regressor.loadRegressor(pwmRegressorPicklePath)
            UsingPwmRegressor.value = False
            PwmRegressorLoaded.value = True
        except (NameError, IOError) as error:
            print(error)
            UsingPwmRegressor.value = False
            PwmRegressorLoaded.value = False
    else:
        print("Regressor Not loaded!")
        UsingPwmRegressor.value = False
        PwmRegressorLoaded.value = False

    
    # Instantiate motors
    leftMotor = Motor(6, 5)
    rightMotor = Motor(26, 13)

    # Main loop
    while True:
        pwmPoint = mathematics.map_to_unit_interval(Lx.value, Ly.value)
        # Decide whether to use the Regressor or the usual way to define the overall pwm of the wheels 
        if(UsingPwmRegressor.value):

            #features = np.asarray([[distF.value, distR.value, distL.value]], dtype=float)
            # features = np.asarray([[distF.value, distR.value, distL.value, steerLeft.value, steerRight.value]], dtype=float)
            features = np.asarray([[distF.value, distR.value, distL.value, ]], dtype=float)
            pwm.value = mathematics.round_to_1_if_greater(pwmRegressor.predict(features))
        

        set_pwm_value(
                        Lx, Ly,
                        pwmPoint, pwm, pwmLeft, pwmRight,
                        UsingPwmRegressor, pwmLeftA, pwmLeftB, pwmRightA, pwmRightB,
                        steerLeft, steerRight, steerFlag
                    )
        update_trim_factors(
                            pwmRight, pwmLeft,
                            ticksRight, ticksLeft,
                            trimFactorRight, trimFactorLeft,
                            frequency,
                            UsingPwmRegressor
                        )
        
        # Updating pwm 
        if(Ly.value < 128):
            leftMotor.stop()
            rightMotor.stop()                        
            leftMotor.forward(abs(pwmLeft.value * (1.0 - (trimFactorLeft.value * steerLeft.value))))
            rightMotor.forward(abs(pwmRight.value * (1.0 - (trimFactorRight.value * steerRight.value))))


        elif(Ly.value > 128):
            leftMotor.stop()
            rightMotor.stop()                            
            leftMotor.backward(abs(pwmLeft.value * (1.0 - (trimFactorLeft.value * steerLeft.value))))
            rightMotor.backward(abs(pwmRight.value * (1.0 - (trimFactorRight.value * steerRight.value))))

        elif(Ly.value == 128):
            if(Lx.value < 128):
                leftMotor.stop()
                rightMotor.stop()                                
                leftMotor.backward(abs(pwmLeft.value * (1.0 - (trimFactorLeft.value * steerLeft.value))))
                rightMotor.forward(abs(pwmRight.value * (1.0 - (trimFactorRight.value * steerRight.value))))

            elif(Lx.value > 128):
                leftMotor.stop()
                rightMotor.stop()                                
                leftMotor.forward(abs(pwmLeft.value * (1.0 - (trimFactorLeft.value * steerLeft.value))))
                rightMotor.backward(abs(pwmRight.value * (1.0 - (trimFactorRight.value * steerRight.value))))

            elif(Lx.value == 128):
                leftMotor.stop()
                rightMotor.stop()

        sleep((1.0/frequency)) 