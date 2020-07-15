import numpy as np
from gpiozero import DistanceSensor, Motor  # Com numeracao BCM
from evdev import InputDevice
import csv
import os
from time import gmtime, strftime, sleep
from multiprocessing import Value, Process

def round(x):
    if(x > 1):
        return 1
    elif(x < 0):
        return 0
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


# inicializa controle
gamepad = InputDevice('/dev/input/event3')
comandos = {(3, 1): 'Ly', (3, 0): 'Lx', (3, 5): 'Ry', (3, 2): 'Rx', (1, 308): 'btn_Y', (1, 307): 'btn_X', (1, 304): 'btn_A', (1, 305): 'btn_B', (1, 310): 'btn_LB', (1, 311): 'btn_RB', (3, 9): 'Rt', (3, 10): 'Lt'}  # accesso: comandos[(event.type,event.code)]
Ly = Value('i', 128, lock=False)
Lx = Value('i', 128, lock=False)

# inicializa motores
motor_esq = Motor(26, 13)
motor_dir = Motor(6, 5)
pwm = Value('d', -1, lock=False)


# inicializa o logging
#logFlag = False
#logFlag = True
logger = Process(target=thread_log, args=(pwm, Lx, Ly))
logger.daemon = True
logger.start()

# inicializa o loop principal
print("Esperando comando:")
for event in gamepad.read_loop():  # polling do controle
    try:
        if(comandos[(event.type, event.code)] == 'Ly'):
            Ly.value = event.value
        elif(comandos[(event.type, event.code)] == 'Lx'):
            Lx.value = event.value
        elif(comandos[(event.type, event.code)] == 'btn_Y'):
            break
        elif(comandos[(event.type, event.code)] == 'btn_A'):
            os.execl('restart.sh', '')
        elif(comandos[(event.type, event.code)] == 'btn_B'):
            calibEsq = calibEsq+0.05
            
        #################
        Lx.value = 128
        Ly.value = 0
        #################        
        Px, Py = conv_quad(Lx.value, Ly.value)
        pwm_point = np.array([Px, Py])
        pwm.value = np.linalg.norm(pwm_point)
        pwm.value = round(pwm.value)
        pwmValueEsq = 0
        calibEsq = 0.0
        pwmValueDir = 0
        calibDir = 0.55

        
        if(Ly.value < 128):
            if(Lx.value < 128):
                pwmValueEsq = abs(pwm.value)
                pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
                pwmValueDir = abs(pwm.value - delta_pwm(pwm_point))
                pwmValueDir = round(pwmValueDir + (calibDir*pwmValueDir))

                motor_esq.forward(pwmValueEsq)
                motor_dir.forward(pwmValueDir)
            
            elif(Lx.value > 128):
                pwmValueEsq = abs(pwm.value - delta_pwm(pwm_point))
                pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
                pwmValueDir = abs(pwm.value)
                pwmValueDir = round(pwmValueDir + (calibDir*pwmValueDir))
                
                motor_esq.forward(pwmValueEsq)
                motor_dir.forward(pwmValueDir)
                
            elif(Lx.value == 128):
                pwmValueEsq = abs(pwm.value)
                pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
                pwmValueDir = abs(pwm.value)
                pwmValueDir = round(pwmValueDir + (calibDir*pwmValueDir))

                motor_esq.forward(pwmValueEsq)
                motor_dir.forward(pwmValueDir)

        elif(Ly.value > 128):
            if(Lx.value < 128):
                pwnValueEsq = abs(pwm.value)
                pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
                pwmValueDir = ((abs(pwm.value - delta_pwm(pwm_point))))
                pwmValueDir = round(pwmValueDir + (calibDir*pwmValueDir))
            
                motor_esq.backward(pwmValueEsq)
                motor_dir.backward(pwmValueDir)
                
            elif(Lx.value > 128):
                pwmValueEsq = abs(pwm.value - delta_pwm(pwm_point))
                pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
                pwmValueDir = abs(pwm.value)
                pwmValueDir = round(pwmValueDir + (calibDir*pwmValueDir))
                
                motor_esq.backward(pwmValueEsq)
                motor_dir.backward(pwmValueDir)

            elif(Lx.value == 128):
                pwmValueEsq = abs(pwm.value)
                pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
                pwmValueDir = abs(pwm.value)
                pwmValueDir = round(pwmValueDir + (calibDir*pwmValueDir))

                motor_esq.backward(pwmValueEsq)
                motor_dir.backward(pwmValueDir)

        elif(Ly.value == 128):
            if(Lx.value < 128):
                pwnValueEsq = abs(pwm.value)
                pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
                pwmValueDir = ((abs(pwm.value - delta_pwm(pwm_point))))
                pwmValueDir = round(pwmValueDir + (calibDir*pwmValueDir))
                
                motor_esq.forward(pwmValueEsq)
                motor_dir.backward(pwmValueDir)

            elif(Lx.value > 128):
                pwmValueEsq = abs(pwm.value - delta_pwm(pwm_point))
                pwmValueEsq = round(pwmValueEsq + (calibEsq*pwmValueEsq))
                pwmValueDir = abs(pwm.value)
                pwmValueDir = round(pwmValueDir + (calibDir*pwmValueDir))
            
                motor_esq.backward(pwmValueEsq)
                motor_dir.forward(pwmValueDir)
                
            elif(Lx.value == 128):
                motor_esq.stop()
                motor_dir.stop()

    except KeyError:
        pass
