#include <stdio.h>
#include <wiringPi.h>


void frente(int pin0A, int pin1A, int pin0B, int pin1B){

    printf("%s\n", "24: H, 25: L");
    digitalWrite(pin0A, HIGH);
    digitalWrite(pin1A, LOW);
    
    printf("%s\n", "23: H, 18: L");
    digitalWrite(pin0B, HIGH);
    digitalWrite(pin1B, LOW);

    delay(1000);

    printf("%s\n", "24: L, 25: L");
    digitalWrite(pin0A, LOW);
    digitalWrite(pin1A, LOW);    

    printf("%s\n", "23: L, 18: L");
    digitalWrite(pin0B, LOW);
    digitalWrite(pin1B, LOW);    

    return;
}   

int main(){
    wiringPiSetupGpio();
    pinMode(18, OUTPUT);    
    pinMode(23, OUTPUT);
    pinMode(24, OUTPUT);
    pinMode(25, OUTPUT);
    
    
    /*delay(3000);
    printf("%s\n", "23: L, 18: L");
    digitalWrite(23,LOW);
    digitalWrite(18,LOW);
    
    delay(3000);
    printf("%s\n", "23: H, 18: L");
    digitalWrite(23,HIGH);
    digitalWrite(18,LOW);
    
    delay(3000);
    printf("%s\n", "23: L, 18: L");    
    digitalWrite(23,LOW);
    digitalWrite(18,LOW);
    
    delay(3000);
    printf("%s\n", "23: L, 18: H");
    digitalWrite(23,LOW);
    digitalWrite(18,HIGH);
    
    delay(3000);
    printf("%s\n", "23: L, 18: L");
    digitalWrite(23,LOW);
    digitalWrite(18,LOW);
    
    printf("%s\n", "\n");
       
    delay(3000);
    printf("%s\n", "24: L, 25: L");
    digitalWrite(24,LOW);
    digitalWrite(25,LOW);
    
    delay(3000);
    printf("%s\n", "24: H, 25: L");
    digitalWrite(24,HIGH);
    digitalWrite(25,LOW);
    
    delay(3000);
    printf("%s\n", "24: L, 25: L");    
    digitalWrite(24,LOW);
    digitalWrite(25,LOW);
    
    delay(3000);
    printf("%s\n", "24: L, 25: H");
    digitalWrite(24,LOW);
    digitalWrite(25,HIGH);
    
    delay(3000);
    printf("%s\n", "24: L, 25: L");
    digitalWrite(24,LOW);
    digitalWrite(25,LOW);*/
 /*   
    digitalWrite(18,LOW); //Direito frente
    digitalWrite(25,LOW); //Esquerdo frentre
    
    digitalWrite(23,HIGH); //Direito frente
    digitalWrite(24,HIGH); //Esquerdo frentre
    
    delay(3000);
    digitalWrite(23,LOW); //Direito frente
    digitalWrite(24,LOW); //Esquerdo frentre*/
    
    
    printf("%s\n", "foward\n");
    delay(3000);
    frente(24, 25, 23, 18);
    
    return 0;
}
