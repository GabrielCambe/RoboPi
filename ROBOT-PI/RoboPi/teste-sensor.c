#include "/home/pi/Documents/RoboPi/include/movimento.h"

#include <ncurses.h>

//MOTORES
#define MOTOR0e 19
#define MOTOR1e 26
//
#define MOTOR0d 13
#define MOTOR1d 6

//SENSORES
#define TRIGfront 2
#define ECHOfront 3
//
#define TRIGdir 18 
#define ECHOdir 23
//
#define TRIGesq 4
#define ECHOesq 17

int main(){
    int ch;

    //Setup dos pinos
    wiringPiSetupGpio();
    //pinMode(MOTOR0A, OUTPUT);    
    //pinMode(MOTOR0B, OUTPUT);
    //pinMode(MOTOR1A, OUTPUT);
    //pinMode(MOTOR1B, OUTPUT);
    pinMode( TRIGG, OUTPUT ) ;
    pinMode( ECHO, INPUT );

    /*
	printf("Esperando input...\n");
    while( (ch = getchar()) != 'x' ){
        switch( ch ){
		printf("Processando input...\n");
            case 'i':
                frente( MOTOR0A, MOTOR1A, MOTOR0B, MOTOR1B );
                break;
            case 'k':
                tras( MOTOR0A, MOTOR1A, MOTOR0B, MOTOR1B );
                break;
            case 'j':
                esquerda( MOTOR0A, MOTOR1A, MOTOR0B, MOTOR1B );
                break;
            case 'l':
                direita( MOTOR0A, MOTOR1A, MOTOR0B, MOTOR1B );
                break;
        }

	//ping( TRIGG, ECHO );
       	
    }*/
    
    while (true){
	ping( TRIGG, ECHO );
	delay( 1000 );
}

        
    return 0;
}
