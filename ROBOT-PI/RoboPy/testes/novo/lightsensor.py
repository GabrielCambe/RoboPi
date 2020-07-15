import RPi.GPIO as GPIO
from multiprocessing import Value, Process
from time import sleep

ticks = Value('i', 0, lock=False)

def pin_changed(ticks):
    print("Pin changed!")
    ticks.value = ticks.value + 1
    print(ticks.value)
    
GPIO.setmode(GPIO.BOARD)
GPIO.setup(5, GPIO.IN)

rise_detect = lambda channel, arg1=ticks: pin_changed(arg1)
GPIO.add_event_detect(5, GPIO.FALLING, callback=rise_detect, bouncetime=200)

while (ticks.value <= 10):
    print("Rodando...", ticks.value)
    sleep(0.5)
    

GPIO.remove_event_detect(23)
print("End...")
