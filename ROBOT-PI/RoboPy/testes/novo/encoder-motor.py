import RPi.GPIO as GPIO
from multiprocessing import Value, Process
from time import sleep
from signal import pause
from gpiozero import DistanceSensor, Motor #A gpioZero trabalha com o sistema de numeracao BCM
from evdev import InputDevice
import csv
from time import sleep

def pin_changed(ticks):
    print("Pin changed!")
    ticks.value = ticks.value + 1
    print(ticks.value)

# inicializa gamepad
#gamepad = InputDevice('/dev/input/event3')
# imprime a informacao do gamepad
# print(gamepad)


comandos = { (3,1):'Ly', (3,0):'Lx', (3,5):'Ry', (3,2):'Rx', (1,308):'btn_Y', (0,0):'Sync' }  #btY.value = 1 => Btn_Y up
# accesso: comandos[(event.type,event.code)]

#inicializa motores
motor_esq = Motor(13, 6, None, True, None)
motor_dir = Motor(19, 26, None, True, None)
velMotorDir = 0.0
velMotorEsq = 0.0

#inicializa sensores
sensrF = DistanceSensor(echo= 18, trigger= 17, max_distance=3)
sensrE = DistanceSensor(echo= 23, trigger= 24, max_distance=3)
sensrD = DistanceSensor(echo= 22, trigger= 27, max_distance=3)


#GPIO.setmode(GPIO.BOARD)
GPIO.setup(2, GPIO.IN)
GPIO.setup(3, GPIO.IN)

ticks1 = Value('i', 0, lock=False)
ticks2 = Value('i', 0, lock=False)

rise1_detect = lambda channel, arg1=ticks1: pin_changed(arg1)
rise2_detect = lambda channel, arg1=ticks2: pin_changed(arg1)

GPIO.add_event_detect(2, GPIO.FALLING, callback=rise1_detect, bouncetime=100)
GPIO.add_event_detect(3, GPIO.FALLING, callback=rise2_detect, bouncetime=100)


print("Esperando comando:")
        
for i in range(255,-1, -1):
    velMotorEsq = (float(128) - float(i))/float(128)
    print("Valor evento: ", i, "VelMotorEsq: ", velMotorEsq)

    velMotorDir = (float(128) - float(i))/float(128)
    print("Valor evento: ", i, "VelMotorDir: ", velMotorDir)

    if(velMotorDir > 0):
        motor_dir.forward( velMotorDir )
    else:
        motor_dir.backward( abs(velMotorDir) )
        
    if(velMotorEsq > 0):
        motor_esq.forward( velMotorEsq )
    else:
        motor_esq.backward( abs(velMotorEsq) )
    sleep(0.5)

for i in range(0,256, 1):
    velMotorEsq = (float(128) - float(i))/float(128)
    print("Valor evento: ", i, "VelMotorEsq: ", velMotorEsq)

    velMotorDir = (float(128) - float(i))/float(128)
    print("Valor evento: ", i, "VelMotorDir: ", velMotorDir)

    if(velMotorDir > 0):
        motor_dir.forward( velMotorDir )
    else:
        motor_dir.backward( abs(velMotorDir) )
        
    if(velMotorEsq > 0):
        motor_esq.forward( velMotorEsq )
    else:
        motor_esq.backward( abs(velMotorEsq) )
    sleep(0.5)
                
#    #Imprime sensores
#    print(sensrF.distance * 100, " cm em F.")
#    print(sensrD.distance * 100, " cm em D.")
#    print(sensrE.distance * 100, " cm em E.")

GPIO.remove_event_detect(2)
GPIO.remove_event_detect(3)

print("End...")

