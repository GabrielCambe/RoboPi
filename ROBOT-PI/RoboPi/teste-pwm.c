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

void setup(){ //Setup dos pinos
    //Setup dos motores
    wiringPiSetupGpio(); // numeração BCM

    if ( ( softPwmCreate(MOTOR0e, 0, 100) ) != 0 ){
        printf("Erro de Setup no pino %d!\n", MOTOR0e);
        abort();
    }
    
    if ( ( softPwmCreate(MOTOR1e, 0, 100) ) != 0 ){
        printf("Erro de Setup no pino %d!\n", MOTOR1e);
        abort();
    }
    
    if ( ( softPwmCreate(MOTOR0d, 0, 100) ) != 0 ){
        printf("Erro de Setup no pino %d!\n", MOTOR0d);
        abort();
    }
    
    if ( ( softPwmCreate(MOTOR1d, 0, 100) ) != 0 ){
        printf("Erro de Setup no pino %d!\n", MOTOR1d);
        abort();
    }
    //**********************

    //Setup dos sensores ultrasônicos
    pinMode( TRIGfront, OUTPUT ) ;
    pinMode( ECHOfront, INPUT );
    
    pinMode( TRIGdir, OUTPUT ) ;
    pinMode( ECHOdir, INPUT );
    
    pinMode( TRIGesq, OUTPUT ) ;
    pinMode( ECHOesq, INPUT );

}

int main(){
    printf("Inicializando...\n");
    setup();    
    
    printf("Começando movimentação...\n");
    
    while ( millis() < 180000 ){
        for ( int i = 30; i <= 100; i+=5 ){
            printf("PWM = %d\n\n", i);
            frentePwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 250, i );
        }
        //int ini = millis();
        //int fim = millis();
        //while( (fim - ini) <= 20000){
          //  fim = millis();
        //}
        for (int i = 100; i >= 30; i-=5){
            printf("PWM = %d\n\n", i);
            frentePwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 250, i );
        }
    }
    
    //INTELIGENCIA 2
    /*
     * float distEsq, distDir, distFron;
    while ( millis() < 12000 ){ // o Robô funciona por cerca de 2min
        //ARVORE DE DECISÃO SIMPLES
        if( (distFron = distancia(TRIGfront, ECHOfront)) > 32 )
            if( (distEsq = distancia( TRIGesq, ECHOesq )) > (distDir = distancia( TRIGdir, ECHOdir )) )
                if( (distEsq - distDir) > 32 )
                    esquerdaPwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 170 );
                else
                    frentePwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 250 );
            else
                if( (distDir - distEsq) > 32 )
                    direitaPwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 170 );
                else
                    frentePwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 250 );
        else
            trasPwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 250 );
            
        
    }
    */
    
    //INTELIGENCIA 1
    /*
        while ( (distEsq = distancia( TRIGesq, ECHOesq )) > 32 && (distDir = distancia( TRIGdir, ECHOdir )) > 32 ){
            frentePwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 250 );
        }
        if ( distEsq >= distDir )
            esquerdaPwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 150 );
        else
            direitaPwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 150 );
    */
        
    printf("Parando...\n");
    pararPwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d );
    
    //while(1){};
        
    return 0 ;
}

/*int main(){
    int ch;
    
    printf("Esperando input...\n");
    while( (ch = getchar()) != 'x' ){
        switch( ch ){
		printf("Processando input...\n");
            case 'i':
                frentePwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 1200 );
                break;
            case 'k':
                trasPwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 1200 );
                break;
            case 'j':
                esquerdaPwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 1200 );
                break;
            case 'l':
                direitaPwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d, 1200 );
                break;
            
            case '\n':
                break;
            
            default:
                printf( "Distance à Frente: %.2f cm.\n\n", distancia( TRIGfront, ECHOfront ) );
                printf( "Distance à Direita: %.2f cm.\n\n", distancia( TRIGdir, ECHOdir ) );
                printf( "Distancia à Esquerda: %.2f cm.\n\n", distancia( TRIGesq, ECHOesq ) );
            break;
        }
    }
    
    printf("Parando...\n");
    pararPwm( MOTOR0e, MOTOR1e, MOTOR0d, MOTOR1d );
        
    return 0;
}
*/

/*
 
 +-----+-----+---------+------+---+---Pi 3B+-+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 |     |     |    3.3v |      |   |  1 || 2  |   |      | 5v      |     |     |
 |   2 |   8 |   SDA.1 |   IN | 1 |  3 || 4  |   |      | 5v      |     |     |
 |   3 |   9 |   SCL.1 |   IN | 1 |  5 || 6  |   |      | 0v      |     |     |
 |   4 |   7 | GPIO. 7 |   IN | 1 |  7 || 8  | 0 | IN   | TxD     | 15  | 14  |
 |     |     |      0v |      |   |  9 || 10 | 1 | IN   | RxD     | 16  | 15  |
 |  17 |   0 | GPIO. 0 |   IN | 0 | 11 || 12 | 0 | IN   | GPIO. 1 | 1   | 18  |
 |  27 |   2 | GPIO. 2 |   IN | 0 | 13 || 14 |   |      | 0v      |     |     |
 |  22 |   3 | GPIO. 3 |   IN | 0 | 15 || 16 | 0 | IN   | GPIO. 4 | 4   | 23  |
 |     |     |    3.3v |      |   | 17 || 18 | 0 | IN   | GPIO. 5 | 5   | 24  |
 |  10 |  12 |    MOSI |   IN | 0 | 19 || 20 |   |      | 0v      |     |     |
 |   9 |  13 |    MISO |   IN | 0 | 21 || 22 | 0 | IN   | GPIO. 6 | 6   | 25  |
 |  11 |  14 |    SCLK |   IN | 0 | 23 || 24 | 1 | IN   | CE0     | 10  | 8   |
 |     |     |      0v |      |   | 25 || 26 | 1 | IN   | CE1     | 11  | 7   |
 |   0 |  30 |   SDA.0 |   IN | 1 | 27 || 28 | 1 | IN   | SCL.0   | 31  | 1   |
 |   5 |  21 | GPIO.21 |   IN | 1 | 29 || 30 |   |      | 0v      |     |     |
 |   6 |  22 | GPIO.22 |   IN | 1 | 31 || 32 | 0 | IN   | GPIO.26 | 26  | 12  |
 |  13 |  23 | GPIO.23 |   IN | 0 | 33 || 34 |   |      | 0v      |     |     |
 |  19 |  24 | GPIO.24 |   IN | 0 | 35 || 36 | 0 | IN   | GPIO.27 | 27  | 16  |
 |  26 |  25 | GPIO.25 |   IN | 0 | 37 || 38 | 0 | IN   | GPIO.28 | 28  | 20  |
 |     |     |      0v |      |   | 39 || 40 | 0 | IN   | GPIO.29 | 29  | 21  |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+---Pi 3B+-+---+------+---------+-----+-----+

 */

