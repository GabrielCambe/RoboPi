import numpy as np
from gpiozero import DistanceSensor, Motor  # Com numeracao BCM
from evdev import InputDevice
import csv
import os
import sys
from time import gmtime, strftime, sleep
from multiprocessing import Value, Process

def round(x):
    if(x > 1):
            return 1
    return x

def thread_log(pwm, Lx, Ly):
    test_name = strftime("teste_%Y-%m-%d_%H:%M:%S_log.csv", gmtime())

    sensrF = DistanceSensor(echo=23, trigger=24, max_distance=3)
    sensrE = DistanceSensor(echo=25, trigger=8, max_distance=3)
    sensrD = DistanceSensor(echo=17, trigger=27, max_distance=3)
    while(True):
        log = [float(Lx.value), float(Ly.value), (sensrF.distance*100),
               (sensrD.distance*100), (sensrE.distance*100), pwm.value]
        print(log)
        with open(test_name, 'ab') as arquivo:
            logger = csv.writer(arquivo)
            logger.writerow(log)
        sleep(0.25)


def conv_quad(x, y):
    """

    O ponto criado por essa funcao indica quais eram os valores dos sensores quando o usuario decidiu mover o carro para frente. 
    Isso pode simbolizar uma relacao de causa e efeito direta.
    """
    Px = ((float(x)-128.0)*(float(x)-128.0))/(128.0*128.0)
    Py = ((float(y)-128.0)*(float(y)-128.0))/(128.0*128.0)
    return (Px, Py)


def delta_pwm(point):
    return (((1.6/np.pi)*(np.arctan2(point[1], point[0]))))

def controle_motores(pwmEsq, pwmDir, Lx, Ly):
    motor_esq = Motor(6, 5)
    motor_dir = Motor(26, 13)
    #GPIO.setup(2, GPIO.IN)
    #GPIO.setup(3, GPIO.IN)

    while True:
        print("pwmEsq: ", pwmEsq.value)
        motor_esq.stop()
        motor_esq.forward(pwmEsq.value)
        print("pwmDir: ", pwmDir.value)
        motor_dir.stop()
        motor_dir.forward(pwmDir.value)
        sleep(0.25)

        
def mudar_velocidade(Lx, Ly, pwm, pwmEsq, pwmDir):
    Px, Py = conv_quad(Lx.value, Ly.value)
    pwm_point = np.array([Px, Py])
    pwm.value = np.linalg.norm(pwm_point)
    
    pwmValueEsq = 0
    calibEsq = 0
    pwmValueDir = 0
    calibDir = 0.07
    
    pwm.value = round(pwm.value)
    
    if(Ly.value < 128):
        if(Lx.value < 128):
            pwmValueEsq = abs(pwm.value)
            pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
            pwmValueDir = abs(pwm.value - delta_pwm(pwm_point))
            pwmValueDir = round(pwmValueDir - (calibDir*pwmValueDir))

            pwmEsq.value = pwmValueEsq
            pwmDir.value = pwmValueDir
            
        elif(Lx.value > 128):
            pwmValueEsq = abs(pwm.value - delta_pwm(pwm_point))
            pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
            pwmValueDir = abs(pwm.value)
            pwmValueDir = round(pwmValueDir - (calibDir*pwmValueDir))
            
            pwmEsq.value = pwmValueEsq
            pwmDir.value = pwmValueDir
                
        elif(Lx.value == 128):
            pwmValueEsq = abs(pwm.value)
            pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
            pwmValueDir = abs(pwm.value)
            pwmValueDir = round(pwmValueDir - (calibDir*pwmValueDir))

            pwmEsq.value = pwmValueEsq
            pwmDir.value = pwmValueDir

    elif(Ly.value > 128):
        if(Lx.value < 128):
            pwnValueEsq = abs(pwm.value)
            pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
            pwmValueDir = abs(pwm.value - delta_pwm(pwm_point))
            pwmValueDir = round(pwmValueDir - (calibDir*pwmValueDir))
            
            pwmEsq.value = pwmValueEsq
            pwmDir.value = pwmValueDir

        elif(Lx.value > 128):
            pwmValueEsq = abs(pwm.value - delta_pwm(pwm_point))
            pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
            pwmValueDir = abs(pwm.value)
            pwmValueDir = round(pwmValueDir - (calibDir*pwmValueDir))

            pwmEsq.value = pwmValueEsq
            pwmDir.value = pwmValueDir

        elif(Lx.value == 128):
            pwmValueEsq = abs(pwm.value)
            pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
            pwmValueDir = abs(pwm.value)
            pwmValueDir = round(pwmValueDir - (calibDir*pwmValueDir))

            pwmEsq.value = pwmValueEsq
            pwmDir.value = pwmValueDir

    elif(Ly.value == 128):
        if(Lx.value < 128):
            pwnValueEsq = abs(pwm.value)
            pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
            pwmValueDir = ((abs(pwm.value - delta_pwm(pwm_point))))
            pwmValueDir = round(pwmValueDir - (calibDir*pwmValueDir))

            pwmEsq.value = pwmValueEsq
            pwmDir.value = pwmValueDir

        elif(Lx.value > 128):
            pwmValueEsq = abs(pwm.value - delta_pwm(pwm_point))
            pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
            pwmValueDir = abs(pwm.value)
            pwmValueDir = round(pwmValueDir - (calibDir*pwmValueDir))

            pwmEsq.value = pwmValueEsq
            pwmDir.value = pwmValueDir

        elif(Lx.value == 128):
            pwmEsq.value = 0
            pwmDir.value = 0
    
# inicializa controle
gamepad = InputDevice('/dev/input/event3')
comandos = {(3, 1): 'Ly', (3, 0): 'Lx', (3, 5): 'Ry', (3, 2): 'Rx', (1, 308): 'btn_Y', (1, 307): 'btn_X', (1, 304): 'btn_A', (1, 305): 'btn_B', (1, 310): 'btn_LB', (1, 311): 'btn_RB', (3, 9): 'Rt', (3, 10): 'Lt'}  # accesso: comandos[(event.type,event.code)]
Ly = Value('i', 128, lock=False)
Lx = Value('i', 128, lock=False)

# inicializa motores

pwm = Value('d', -1, lock=False)
pwmEsq = Value('d', 0, lock=False)
pwmDir = Value('d', 0, lock=False)

# inicializa o logging
#logFlag = False
#logFlag = True
#logger = Process(target=thread_log, args=(pwm, Lx, Ly))
#logger.daemon = True
#logger.start()

acelerador = Process(target=controle_motores, args=(pwmEsq, pwmDir, Lx, Ly))
acelerador.daemon = True
acelerador.start()

# inicializa o loop principal
print("Esperando comando:")
for event in gamepad.read_loop():  # polling do controle
    try:
        if(comandos[(event.type, event.code)] == 'Ly'):
            #Ly.value = event.value
            Ly.value = 0
            mudar_velocidade(Lx, Ly, pwm, pwmEsq, pwmDir)
        elif(comandos[(event.type, event.code)] == 'Lx'):
            #Lx.value = event.value
            Lx.value = 128
            mudar_velocidade(Lx, Ly, pwm, pwmEsq, pwmDir)
        elif(comandos[(event.type, event.code)] == 'btn_Y'):
            #break
            #################
            Lx.value = 128
            Ly.value = 128
            #################        
            mudar_velocidade(Lx, Ly, pwm, pwmEsq, pwmDir)
            sleep(1)
            sys.exit()
        elif(comandos[(event.type, event.code)] == 'btn_A'):
            os.execl('restart.sh', '')

            
    except KeyError:
        pass
