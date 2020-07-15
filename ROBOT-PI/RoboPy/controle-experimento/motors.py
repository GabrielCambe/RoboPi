from gpiozero import Motor  # this library uses BCM numbering for the Pi's pins
from time import sleep
import RPi.GPIO as GPIO
from multiprocessing import Value
import sys

import motorcontrol

#def distance_from_ticks(ticks):
#    wheelCircumference = 20.5 # in centimeters
#    ticksPerRotation = 20.0
#    distanceForTick = wheelCircumference/tickPerRotation

#    return ticks*distanceForTick

    
#print('Distance: ' + str(distance_from_ticks(ticksRight.value)))
#print('Distance: ' + str(distance_from_ticks(ticksRight.value)))
#print('RPM: ')
#print('RPM: ')


# Instantiate motors
leftMotor = Motor(6, 5)
rightMotor = Motor(26, 13)

# Set the optic sensors's input pins. They are the reason this function can calculate the wheels's rotation and correct it
GPIO.setup(2, GPIO.IN)
GPIO.setup(3, GPIO.IN)

# Defining and initializing the variables for counting the wheels encoder ticks
ticksRight = Value('i', 0, lock=False)
ticksLeft = Value('i', 0, lock=False)

# Creating the callback functions for the optic encoder interrupts
riseRight_detect = lambda channel, arg1=ticksRight: motorcontrol.ticks_pin_changed(arg1)
riseLeft_detect = lambda channel, arg1=ticksLeft: motorcontrol.ticks_pin_changed(arg1)

GPIO.add_event_detect(2, GPIO.FALLING, callback=riseRight_detect, bouncetime=25)
GPIO.add_event_detect(3, GPIO.FALLING, callback=riseLeft_detect, bouncetime=25)

try:
    testIterations = int(sys.argv[1])
except IndexError:
    testIterations = 10
    
# FInd max PWM for wheels in relation to the slowest wheel
pwmLeft = 1.0
pwmRight = 1.0

hitsLeft = 0
hitsRight = 0

#slowestWheel = ''

print('Finding slowest wheel...')
for i in range(0,testIterations):
    leftMotor.forward(pwmLeft)
    rightMotor.forward(pwmRight)
    sleep(1)
    leftMotor.stop()
    rightMotor.stop()
    
    print('Left ticks/s:' + str(ticksLeft.value) + ' Right ticks/s:' + str(ticksRight.value))
    if(ticksLeft.value == ticksRight.value):
        pass
    elif(ticksLeft.value > ticksRight.value):
        hitsLeft = hitsLeft + 1 
    elif(ticksRight.value > ticksLeft.value):
        hitsRight = hitsRight + 1

    ticksLeft.value = 0
    ticksRight.value = 0

if(hitsLeft > hitsRight):
    pwmRightA = 0.0
    pwmRightB = 1.0
    slowestWheel = 'RightWheel'
    print('The slowes wheel is the ' + slowestWheel)
elif(hitsLeft < hitsRight):
    pwmLeftA = 0.0
    pwmLeftB = 1.0
    slowestWheel = 'LeftWheel'
    print('The slowes wheel is the ' + slowestWheel)
else:
    print("As rodas tem velocidades iguais!!")
    print("Aumente o tempo de teste se nao estiver satisfeito.")
    sys.exit()


print('\n')
print('Finding fastest wheel\'s Max PWM...')
pwmA = 0.0
pwmB = 1.0
#pwm = 1.0
pwm = pwmA + ((pwmB - pwmA)/2.0)

while((pwmB - pwmA) >= 0.00390625):

    hits = 0
    hitsLeft = 0
    hitsRight = 0
    
    for i in range(0,testIterations):
        if(slowestWheel == 'RightWheel'):
            leftMotor.forward(pwm)
            rightMotor.forward(pwmRight)
        elif(slowestWheel == 'LeftWheel'):
            leftMotor.forward(pwmLeft)
            rightMotor.forward(pwm)

        sleep(1)
        leftMotor.stop()
        rightMotor.stop()
        
        print('Left ticks/s:' + str(ticksLeft.value) + ' Right ticks/s:' + str(ticksRight.value))
    
        if(ticksLeft.value == ticksRight.value):
            hits = hits + 1
        elif(ticksLeft.value > ticksRight.value):
            hitsLeft = hitsLeft + 1 
        elif(ticksRight.value > ticksLeft.value):
            hitsRight = hitsRight + 1

        ticksLeft.value = 0
        ticksRight.value = 0

    if(hits < testIterations):
        if(slowestWheel == 'RightWheel'):
            if(hitsLeft > hitsRight):
                #pwmA = pwm
                pwmB = pwm
                pwm = pwmA + ((pwmB - pwmA)/2.0)
            elif(hitsLeft < hitsRight):
                pwmA = pwm
                pwm = pwmA + ((pwmB - pwmA)/2.0)
            else:
                print("Comportamento Indefinido!!")
                sys.exit()

        elif(slowestWheel == 'LeftWheel'):
            if(hitsLeft > hitsRight):
                pwmA = pwm
                pwm = pwmA + ((pwmB - pwmA)/2.0)
                
            elif(hitsLeft < hitsRight):
                pwmB = pwm
                pwm = pwmA + (pwmB - pwmA)/2.0

            else:
                print("Comportamento Indefinido!!")
                sys.exit()

                
    if(slowestWheel == 'RightWheel'):
        print('Max PWM Left in {' + str(pwmA) + ',' + str(pwmB) + '}.')
       
    elif(slowestWheel == 'LeftWheel'):
        print('Max PWM Right in {' + str(pwmA) + ',' + str(pwmB) + '}.')

print('\n')
if(slowestWheel == 'RightWheel'):
    pwmLeftA = 0.0
    pwmLeftB = pwmA + (pwmB - pwmA)/2.0
    #print('PWM Left in {' + str(pwmLeftA) + ',' + str(pwmLeftB) + '}.')
    #print('PWM Right in {' + str(pwmRightA) + ',' + str(pwmRightB) + '}.')
    print('Max valid PWM Left: ' + str(pwmLeftB) + '.')
    
elif(slowestWheel == 'LeftWheel'):
    pwmRightA = 0.0
    pwmRightB = pwmA + (pwmB - pwmA)/2.0
    #print('PWM Left in {' + str(pwmLeftA) + ',' + str(pwmLeftB) + '}.')
    #print('PWM Right in {' + str(pwmRightA) + ',' + str(pwmRightB) + '}.')
    print('Max valid PWM Right: ' + str(pwmRightB) + '.')



print('\n')
print('Finding the wheels\'s Min PWM...')

pwmRight = 0.0
pwmLeft = 0.0
pwmIncrement = 1.0/testIterations
ticksLeft.value = 0
ticksRight.value = 0


print('Finding feasible min values for wheels PWM...')
while(ticksLeft.value == 0 or ticksRight.value == 0):
    pwmRight =  pwmRight + pwmIncrement
    pwmLeft =  pwmLeft + pwmIncrement
    leftMotor.forward(pwmLeft)
    rightMotor.forward(pwmRight)
    sleep(1)
    print('PWM Left: ' + str(pwmLeft))
    print('PWM Right: ' + str(pwmRight))
    

print('\n')
print('Finding the wheels\'s Min PWM...')

pwmRightAA = 0.0
pwmRightAB = pwmRight
pwmRight = pwmRightAA + ((pwmRightAB - pwmRightAA)/2.0)

pwmLeftAA = 0.0
pwmLeftAB = pwmLeft
pwmLeft = pwmLeftAA + ((pwmLeftAB - pwmLeftAA)/2.0)

while((pwmRightAB - pwmRightAA) >= 0.00390625 or (pwmLeftAB - pwmLeftAA) >= 0.00390625):
    leftMotor.forward(pwmLeft)
    rightMotor.forward(pwmRight)
    sleep(1)
    leftMotor.stop()
    rightMotor.stop()
    
    print('Left ticks/s:' + str(ticksLeft.value) + ' Right ticks/s:' + str(ticksRight.value))
    print('PWM Left: ' + str(pwmLeft))
    print('PWM Right: ' + str(pwmRight))

            
    if(ticksRight.value != 0):
        pwmRightAB = pwmRight
        pwmRight =  + ((pwmRightAB - pwmRightAA)/2.0)
            
    else:
        pwmRightAA = pwmRight
        pwmRight = pwmRightAA + ((pwmRightAB - pwmRightAA)/2.0)
        

    if(ticksLeft.value != 0):
        pwmLeftAB = pwmLeft
        pwmLeft =  + ((pwmLeftAB - pwmLeftAA)/2.0)
            
    else:
        pwmLeftAA = pwmLeft
        pwmLeft = pwmLeftAA + ((pwmLeftAB - pwmLeftAA)/2.0)

        
    print('Min PWM Left in {' + str(pwmLeftAA) + ',' + str(pwmLeftAB) + '}.')   
    print('Min PWM Right in {' + str(pwmRightAA) + ',' + str(pwmRightAB) + '}.')
        
        
    ticksLeft.value = 0
    ticksRight.value = 0

    
    
print('PWM Left in {' + str(pwmLeftAA) + ',' + str(pwmLeftB) + '}.')
print('PWM Right in {' + str(pwmRightAA) + ',' + str(pwmRightB) + '}.')
