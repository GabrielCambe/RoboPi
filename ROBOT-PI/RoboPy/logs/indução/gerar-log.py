import pandas
from time import sleep
import sys
import numpy 

column_names = ["gamepadLx","gamepadLy","frontSensor","rightSensor","leftSensor","pwm","pwmLeft","pwmRight"]    
df = pandas.DataFrame(columns=column_names)

frente = 180.0
esquerdaMenor = 30.0
direitaMenor = 30.0
esquerdaMaior = 60.0
direitaMaior = 60.0
esquerdaDiferenca = esquerdaMaior - esquerdaMenor 
direitaDiferenca = direitaMaior - direitaMenor

corredorMenor = esquerdaMenor + direitaMenor
corredorMaior = esquerdaMaior + direitaMaior
distanciaSegura = 15.0
centro = numpy.random.uniform(low=(distanciaSegura), high=(corredorMenor-distanciaSegura))

esquerdaMenor =  centro
direitaMenor = corredorMenor - esquerdaMenor
esquerdaMaior = esquerdaDiferenca + esquerdaMenor
direitaMaior = corredorMaior - esquerdaMaior

frequencia = 512.0

while(frente > 0.0):
    if(frente <= 25.0):
        esquerda = esquerdaMenor
        direita = direitaMenor
        pwm = 0.0
        frente = frente - 2.0

    elif(frente <= 60.0):
        esquerda = esquerdaMenor
        direita = direitaMenor
        pwm = 0.5
        distancia_percorrida = pwm * (60/frequencia) # 2 segundos para atravessar 60cm em velocidade 0.5
        frente = frente - distancia_percorrida

    elif(frente <= 120.0):
        esquerda = esquerdaMaior
        direita = direitaMaior
        pwm = 1.0
        distancia_percorrida = pwm * (60/frequencia) # 2 segundos para atravessar 60cm em velocidade 0.5
        frente = frente - distancia_percorrida


    elif(frente <= 180.0):
        esquerda = esquerdaMenor
        direita = direitaMenor
        pwm = 0.5
        distancia_percorrida = pwm * (60/frequencia) # 2 segundos para atravessar 60cm em velocidade 0.5
        frente = frente - distancia_percorrida


    df = df.append({'frontSensor': frente, 'rightSensor': direita, 'leftSensor': esquerda, 'pwm': pwm}, ignore_index=True)
    sleep(1.0/frequencia)

try:
    df.to_csv("log_sintetico" + sys.argv[1] + ".csv", index = False)
except IndexError as error:
    df.to_csv("log_sintetico.csv", index = False)


