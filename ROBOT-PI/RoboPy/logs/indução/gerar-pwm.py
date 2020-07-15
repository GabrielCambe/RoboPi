import pandas
from time import sleep
import sys
import numpy 

for csvFile in sys.argv[1:]:
    auxDf = pandas.read_csv(csvFile)
    column_names = ["gamepadLx","gamepadLy","frontSensor","rightSensor","leftSensor","pwm","pwmLeft","pwmRight"]    
    df = pandas.DataFrame(columns=column_names)
    
    corredorMenor = 60.0
    corredorMaior = 120.0

    for index, row in auxDf.iterrows():
        #row['frontSensor']
        #row['rightSensor']
        #row['leftSensor']
        #row['pwm']
        pwm = (row['rightSensor'] + row['leftSensor'])/corredorMaior
        df = df.append({'frontSensor': row['frontSensor'], 'rightSensor': row['rightSensor'], 'leftSensor': row['leftSensor'], 'pwm': pwm}, ignore_index=True)
    df.to_csv("pwm_sintetico_" + csvFile, index = False)
