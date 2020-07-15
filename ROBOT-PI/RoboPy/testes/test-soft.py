from signal import pause
from gpiozero import DistanceSensor, Motor #A gpioZero trabalha com o sistema de numeracao BCM
from evdev import InputDevice
import csv


# inicializa gamepad
gamepad = InputDevice('/dev/input/event3')
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

print("Esperando comando:")

for event in gamepad.read_loop(): #polling do controle
    try:
        if(comandos[(event.type,event.code)] == 'Ly' ):
            velMotorEsq = (1.0/(4.0*4096.0))*pow(float(128.0) - float(event.value),2)
            if(event.value < 128):
                motor_esq.forward( velMotorEsq )
            else:
                motor_esq.backward( velMotorEsq )
            
            print("VelMotorEsq: ", velMotorEsq)
        elif(comandos[(event.type,event.code)] == 'Ry' ):
            velMotorDir = (1.0/(4.0*4096.0))*pow(float(128.0) - float(event.value),2)
            if(event.value < 128):
                motor_dir.forward( velMotorDir )
            else:
                motor_dir.backward( velMotorDir )

#            velMotorDir = (float(128) - float(event.value))/float(128)
            print("VelMotorDir: ", velMotorDir)
        elif(comandos[(event.type,event.code)] == 'btn_Y' ):
            break
    except KeyError:
        print("Comando nao catalogado!")

        
        
    #Imprime sensores
    print(sensrF.distance * 100, " cm em F.")
    print(sensrD.distance * 100, " cm em D.")
    print(sensrE.distance * 100, " cm em E.")
