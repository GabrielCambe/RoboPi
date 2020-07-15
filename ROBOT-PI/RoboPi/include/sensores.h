#ifndef SENSORES_H
#define SENSORES_H

#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int pulso( int trig, int echo, float *distance );
float distancia( int trig, int echo );

#endif
