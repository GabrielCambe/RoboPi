#include "/home/pi/Documents/RoboPi/include/movimento.h"

void tras( int pin0A, int pin1A, int pin0B, int pin1B, int delayTime ){
    printf( "%d: L, %d: H\n", pin0A, pin1A );
    digitalWrite( pin0A, LOW );
    digitalWrite( pin1A, HIGH );
    
    printf( "%d: L, %d: H\n", pin0B, pin1B );
    digitalWrite( pin0B, LOW );
    digitalWrite( pin1B, HIGH );

    delay( delayTime );
    parar( pin0A, pin1A, pin0B, pin1B );
    

    return;
}  
