#include "/home/pi/Documents/RoboPi/include/movimento.h"

#include <ncurses.h>

//
#define MOTOR0A 4
#define MOTOR1A 17
//
#define MOTOR0B 22
#define MOTOR1B 27
#define TRIGG 23
#define ECHO 24

static int ping( int trig, int echo ){
	long int ping = 0;
	long int pong = 0;
	float distance = 0;
 	long int timeout = 500000; // 0.5 sec
	
	// Ensure trigger is low.
	digitalWrite( trig, LOW );
	delay( 100 ); //50
	
	// trigger the ping.
	digitalWrite( trig, HIGH );
	delayMicroseconds( 60 ); //30
	digitalWrite( trig, LOW );
	
	long int start_time, end_time;
	
	start_time = micros();
	end_time = micros();
	// Wait for ping response, or timeout.
	while ( digitalRead( echo ) == LOW && (end_time - start_time) < timeout ){
		end_time = micros();
	}
	
	// Cancel on timeout.
	if ( (end_time - start_time) > timeout ){
		printf("Out of range.\n");
		return 0;
	}
	
	ping = micros();
	
	start_time = micros();
	end_time = micros();
	// Wait for pong response, or timeout.
	while (digitalRead(echo) == HIGH && (end_time - start_time) < timeout){}
	
	// Cancel on timeout.
	if ( (end_time - start_time) > timeout ){
		printf("Out of range.\n");
		return 0;
	}
	
	pong = micros();
	
	// Convert ping duration to distance.
	distance = (float) (pong - ping) * 0.017150;
	
	printf( "Distance: %.2f cm.\n", distance );
	
	return 1;
}


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
