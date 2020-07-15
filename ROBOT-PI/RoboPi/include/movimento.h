#ifndef MOVIMENTO_H
#define MOVIMENTO_H

#include <wiringPi.h>
#include <softPwm.h> //PWM do WiringPi
#include <stdio.h>
//#include <stdlib.h>
//#include <stdint.h>

void frente( int pin0A, int pin0b, int pin1a, int pin1B, int delayTime );
void tras( int pin0A, int pin1A, int pin0B, int pin1B, int delayTime );
void esquerda( int pin0A, int pin1A, int pin0B, int pin1B, int delayTime );
void direita( int pin0A, int pin1A, int pin0B, int pin1B, int delayTime );
void parar( int pin0A, int pin1A, int pin0B, int pin1B );

void frentePwm( int pin0A, int pin0b, int pin1a, int pin1B, int delayTime, int PWMvalue );
void trasPwm( int pin0A, int pin1A, int pin0B, int pin1B, int delayTime );
void esquerdaPwm( int pin0A, int pin1A, int pin0B, int pin1B, int delayTime );
void direitaPwm( int pin0A, int pin1A, int pin0B, int pin1B, int delayTime );
void pararPwm( int pin0A, int pin1A, int pin0B, int pin1B );


#endif
