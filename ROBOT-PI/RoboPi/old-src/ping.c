#include "/home/pi/Documents/RoboPi/include/sensores.h"

int pulse( int trig, int echo, float *distance ){
	long int ping = 0;
	long int pong = 0;
	*distance = 0;
 	long int timeout = 500000; // 0.5 sec
	
	// Ensure trigger is low.
	digitalWrite( trig, LOW );
	delay( 50 ); //50
	
	// trigger the ping.
	digitalWrite( trig, HIGH );
	delayMicroseconds( 30 ); //30
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
	*distance = (float) (pong - ping) * 0.017150;
	
	//printf( "Distance: %.2f cm.\n", *distance );
	
	return 1;
}
