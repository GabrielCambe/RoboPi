#include "/home/pi/Documents/RoboPi/include/movimento.h"
#include "/home/pi/Documents/RoboPi/include/sensores.h"
#include <stdio.h>

//
#define MOTOR0A 4
#define MOTOR1A 17
//
#define MOTOR0B 22
#define MOTOR1B 27
#define TRIGG 23
#define ECHOleft 24
#define ECHOright 25

int main(){
    int ch;

    //Setup dos pinos
    wiringPiSetupGpio();
    pinMode(MOTOR0A, OUTPUT);    
    pinMode(MOTOR0B, OUTPUT);
    pinMode(MOTOR1A, OUTPUT);
    pinMode(MOTOR1B, OUTPUT);
    pinMode( TRIGG, OUTPUT ) ;
    pinMode( ECHOleft, INPUT );
    pinMode(ECHOright, INPUT);

    
    printf("Esperando input...\n");
    while( (ch = getchar()) != 'x' ){
        switch( ch ){
		printf("Processando input...\n");
            case 'i':
                frente( MOTOR0A, MOTOR1A, MOTOR0B, MOTOR1B, 300 );
                break;
            case 'k':
                tras( MOTOR0A, MOTOR1A, MOTOR0B, MOTOR1B, 300 );
                break;
            case 'j':
                esquerda( MOTOR0A, MOTOR1A, MOTOR0B, MOTOR1B, 300 );
                break;
            case 'l':
                direita( MOTOR0A, MOTOR1A, MOTOR0B, MOTOR1B, 300 );
                break;
        }

//	    printf( "Distance: %.2f cm.\n", distance( TRIGG, ECHOleft ) );
        printf( "Distance: %.2f cm.\n", distancia( TRIGG, ECHOright ) );
    }
        
    return 0;
}
