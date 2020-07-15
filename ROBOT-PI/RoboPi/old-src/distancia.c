#include "/home/pi/Documents/RoboPi/include/sensores.h"

float distancia( int trig, int echo ){
	float distance; pulse( trig, echo, &distance ) ? return distance : return -1 ;
}
