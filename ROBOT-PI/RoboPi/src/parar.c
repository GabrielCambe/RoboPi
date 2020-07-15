#include "/home/pi/Documents/RoboPi/include/movimento.h"

void parar(int pin0A, int pin1A, int pin0B, int pin1B){
    printf("%d: L, %d: L\n", pin0A, pin1A);
    digitalWrite(pin0A, LOW);
    digitalWrite(pin1A, LOW);
    
    printf("%d: L, %d: L\n", pin0B, pin1B);
    digitalWrite(pin0B, LOW);
    digitalWrite(pin1B, LOW);

    return;
}  
