#include "/home/pi/Documents/RoboPi/include/movimento.h"

void frentePwm( int pin0A, int pin1A, int pin0B, int pin1B, int delayTime, int PWMvalue ){
    printf( "%d: H, %d: L\n", pin0A, pin1A );
    softPwmWrite( pin0A, PWMvalue );
    softPwmWrite( pin1A, 0 );
    
    printf( "%d: H, %d: L\n", pin0B, pin1B );
    softPwmWrite( pin0B, PWMvalue );
    softPwmWrite( pin1B, 0 );

    delay( delayTime );
    pararPwm( pin0A, pin1A, pin0B, pin1B );

    return;
}  

void direitaPwm( int pin0A, int pin1A, int pin0B, int pin1B, int delayTime ){
    printf( "%d: H, %d: L\n", pin0A, pin1A );
    softPwmWrite( pin0A, 100 );
    softPwmWrite( pin1A, 0 );
    
    printf( "%d: H, %d: L\n", pin0B, pin1B );
    softPwmWrite( pin0B, 50 );
    softPwmWrite( pin1B, 0 );

    delay( delayTime );
    pararPwm( pin0A, pin1A, pin0B, pin1B );
    
    return;
}  

void esquerdaPwm( int pin0A, int pin1A, int pin0B, int pin1B, int delayTime ){
    printf( "%d: H, %d: L\n", pin0A, pin1A );
    softPwmWrite( pin0A, 50 );
    softPwmWrite( pin1A, 0 );
    
    printf( "%d: H, %d: L\n", pin0B, pin1B );
    softPwmWrite( pin0B, 100 );
    softPwmWrite( pin1B, 0 );

    delay( delayTime );
    pararPwm( pin0A, pin1A, pin0B, pin1B );

    return;
}  

void trasPwm( int pin0A, int pin1A, int pin0B, int pin1B, int delayTime ){
    printf( "%d: L, %d: H\n", pin0A, pin1A );
    softPwmWrite( pin0A, 0 );
    softPwmWrite( pin1A, 100 );
    
    printf( "%d: L, %d: H\n", pin0B, pin1B );
    softPwmWrite( pin0B, 0 );
    softPwmWrite( pin1B, 100 );

    delay( delayTime );
    pararPwm( pin0A, pin1A, pin0B, pin1B );
    

    return;
}  

void pararPwm(int pin0A, int pin1A, int pin0B, int pin1B){
    printf("%d: L, %d: L\n", pin0A, pin1A);
    softPwmWrite(pin0A, 0);
    softPwmWrite(pin1A, 0);
    
    printf("%d: L, %d: L\n", pin0B, pin1B);
    softPwmWrite(pin0B, 0);
    softPwmWrite(pin1B, 0);

    return;
}  
