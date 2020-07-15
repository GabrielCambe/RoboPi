#include <stdio.h>
#include <wiringPi.h>

int main(){
    wiringPiSetupGpio();
    //CINZA 24
    pinMode(23, OUTPUT);
    //LARANJA 23    
    pinMode(24, OUTPUT);
    delay(3000);
    digitalWrite(23,LOW);
    digitalWrite(24,LOW);
    delay(3000);
    digitalWrite(23,HIGH);
    digitalWrite(24,LOW);
    delay(3000);
    digitalWrite(23,LOW);
    digitalWrite(24,LOW);
    delay(3000);
    
    digitalWrite(23,LOW);
    digitalWrite(24,HIGH);

    return 0;
}
