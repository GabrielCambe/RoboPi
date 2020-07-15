#include "/home/pi/Documents/RoboPi/include/movimento.h"
#include "/home/pi/Documents/RoboPi/include/sensores.h"
#include <stdio.h>

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

void setup(){
     //Setup dos pinos
    wiringPiSetupGpio(); // BCM numbering
    pinMode(MOTOR0e, OUTPUT);
    pinMode(MOTOR1e, OUTPUT);
        
    pinMode(MOTOR0d, OUTPUT);
    pinMode(MOTOR1d, OUTPUT);
    
    pinMode( TRIGfront, OUTPUT ) ;
    pinMode( ECHOfront, INPUT );
    
    pinMode( TRIGdir, OUTPUT ) ;
    pinMode( ECHOdir, INPUT );
    
    pinMode( TRIGesq, OUTPUT ) ;
    pinMode( ECHOesq, INPUT );
    //**********************

}

int main(){
    printf("Inicializando...\n");
    setup();    
    
    printf("Começando movimentação...\n");
    float distEsq, distDir;
    while ( millis() < 6000 ){ // o Robô funciona por cerca de um minutos
        while ( (distEsq = distancia( TRIGG, ECHOleft )) > 32 && (distDir = distancia( TRIGG, ECHOright )) > 32 ){
            frente( MOTOR0A, MOTOR1A, MOTOR0B, MOTOR1B, 250 );
        }
        if ( distEsq >= distDir )
            esquerda( MOTOR0A, MOTOR1A, MOTOR0B, MOTOR1B, 250 );
        else
            direita( MOTOR0A, MOTOR1A, MOTOR0B, MOTOR1B, 250 );
    }
    printf("Parando...\n");
    parar(  MOTOR0A, MOTOR1A, MOTOR0B, MOTOR1B );
    return 0 ;
}
