#include "/home/pi/Documents/RoboPi/include/movimento.h"

void frente( int pin0A, int pin1A, int pin0B, int pin1B, int delayTime ){
    printf( "%d: H, %d: L\n", pin0A, pin1A );
    digitalWrite( pin0A, HIGH );
    digitalWrite( pin1A, LOW );
    
    printf( "%d: H, %d: L\n", pin0B, pin1B );
    digitalWrite( pin0B, HIGH );
    digitalWrite( pin1B, LOW );

    delay( delayTime );
    parar( pin0A, pin1A, pin0B, pin1B );

    return;
}  
