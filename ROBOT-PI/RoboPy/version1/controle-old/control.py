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
import RPi.GPIO as GPIO
import sys
import numpy as np

#from mathematics import map_to_unit_interval, round_to_1_if_greater
import mathematics
#from motorcontrol import thread_reset_factors, ticks_pin_changed, thread_reset_ticks, set_pwm_value, thread_motors_controller
import motorcontrol
#from distancelog import thread_log 
import distancelog

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
#motorsProcess = Process(target=motorcontrol.thread_motors_controller, args=(ticksRight, ticksLeft, trimFactorRight, trimFactorLeft, pwmLeft, pwmRight, Lx, Ly))
#motorsProcess.daemon = True
#motorsProcess.start()

# Initialize the logging process
logProcess = Process(target=distancelog.thread_log, args=(pwm, pwmLeft, pwmRight, trimFactorLeft, trimFactorRight, Lx, Ly))
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

riseRight_detect = lambda channel, arg1=ticksRight: motorcontrol.ticks_pin_changed(arg1)
riseLeft_detect = lambda channel, arg1=ticksLeft: motorcontrol.ticks_pin_changed(arg1)

GPIO.add_event_detect(2, GPIO.FALLING, callback=riseRight_detect, bouncetime=25)
GPIO.add_event_detect(3, GPIO.FALLING, callback=riseLeft_detect, bouncetime=25)

# # Initialize the trajectory correction process
#encodersProcess = Process(target=thread_encoders,args=(ticksRight, ticksLeft, pwmRight, pwmLeft, trimFactorRight, trimFactorLeft))
#encodersProcess.daemon = True
#encodersProcess.start()

# Motor controlling process
motorsProcess = Process(target=motorcontrol.thread_motors_controller, args=(ticksRight, ticksLeft, trimFactorRight, trimFactorLeft, pwmRight, pwmLeft, Lx, Ly))
motorsProcess.daemon = True
motorsProcess.start()

# ...
resetFactorsProcess = Process(target=motorcontrol.thread_reset_factors, args=(trimFactorRight, trimFactorLeft))
resetFactorsProcess.daemon = True
resetFactorsProcess.start()

# ...
resetTicksProcess = Process(target=motorcontrol.thread_reset_ticks, args=(ticksRight, ticksLeft))
resetTicksProcess.daemon = True
resetTicksProcess.start()




# Initialize the gamepad
gamepad = InputDevice('/dev/input/event3')
commands = {(3, 1): 'Ly', (3, 0): 'Lx', (3, 5): 'Ry', (3, 2): 'Rx', (1, 308): 'btn_Y', (1, 307): 'btn_X', (1, 304): 'btn_A', (1, 305): 'btn_B', (1, 310): 'btn_LB', (1, 311): 'btn_RB', (3, 9): 'Rt', (3, 10): 'Lt'}  # accesso: commands[(event.type,event.code)]

print("Awaiting commands:")
print('btn_Y: Exit the program')
print('btn_A: Stop/Start new log')
print('btn_LB: Go in a straight line (for calibration tests)')
print('btn_RB: Stops the calibration test and returns to the outer loop')

# Main loop based on pooling the gamepad
for event in gamepad.read_loop():
    try:
        if(commands[(event.type, event.code)] == 'Ly'): # Update Ly and the general PWM value
            Ly.value = event.value
            pwmPoint = mathematics.map_to_unit_interval(Lx.value, Ly.value)
            pwm.value = mathematics.round_to_1_if_greater(np.linalg.norm(pwmPoint))
            # Set the PWM value for each motor
            motorcontrol.set_pwm_value(Lx, Ly, pwmPoint, pwm, pwmLeft, pwmRight, trimFactorRight, trimFactorLeft, ticksRight, ticksLeft)

            
        elif(commands[(event.type, event.code)] == 'Lx'): # Update Lx and the PWM value
            Lx.value = event.value
            pwmPoint = mathematics.map_to_unit_interval(Lx.value, Ly.value)
            pwm.value = mathematics.round_to_1_if_greater(np.linalg.norm(pwmPoint))
            # Set the PWM value for each motor
            motorcontrol.set_pwm_value(Lx, Ly, pwmPoint, pwm, pwmLeft, pwmRight, trimFactorRight, trimFactorLeft, ticksRight, ticksLeft)

            
        elif(commands[(event.type, event.code)] == 'btn_Y'): # Exit the program
            # Terminate log process if active 
            if(logFlag):
                logProcess.terminate()
            # Stop the motors and terminate the motors process by simulating a command on the gamepad
            Lx.value = 128
            Ly.value = 128
            motorcontrol.set_pwm_value(Lx, Ly, pwmPoint, pwm, pwmLeft, pwmRight, trimFactorRight, trimFactorLeft, ticksRight, ticksLeft)
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
                    logProcess = Process(target=distancelog.thread_log, args=(pwm, pwmLeft, pwmRight, trimFactorLeft, trimFactorRight, Lx, Ly))
                    logProcess.daemon = True
                    logProcess.start()
                    logFlag = True
                btnAclean = False
            else:
                btnAclean = True

                
        elif(commands[(event.type, event.code)] == 'btn_LB'): # Go in a straight line (for calibration tests)
            # Simulates the joystick position that tells the prototype to go straight forward
            Ly.value = 0
            Lx.value = 128
            pwmPoint = mathematics.map_to_unit_interval(Lx.value, Ly.value)
            pwm.value = mathematics.round_to_1_if_greater(np.linalg.norm(pwmPoint))
            # Set the PWM value for each motor
            motorcontrol.set_pwm_value(Lx, Ly, pwmPoint, pwm, pwmLeft, pwmRight, trimFactorRight, trimFactorLeft, ticksRight, ticksLeft)            
            for subEvent in gamepad.read_loop(): # Inside loop that waits for the command to stop the calibration    
                try:
                    if(commands[(subEvent.type, subEvent.code)] == 'btn_RB'): # Stops the calibration test and returns to the outer loop
                        Lx.value = 128
                        Ly.value = 128
                        motorcontrol.set_pwm_value(Lx, Ly, pwmPoint, pwm, pwmLeft, pwmRight, trimFactorRight, trimFactorLeft, ticksRight, ticksLeft)
                        break
                except KeyError: # Keeps going forward otherwise
                    pass
        elif(commands[(event.type, event.code)] == 'btn_B'): #
            print('btn_B\n')
            
        elif(commands[(event.type, event.code)] == 'btn_X'): # 
            print('btn_X\n')
            
    except KeyError:
        pass
