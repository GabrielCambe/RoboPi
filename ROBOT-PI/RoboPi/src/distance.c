#include "/home/pi/Documents/RoboPi/include/sensores.h"

float distance( int trig, int echo ){
		float distance;
		if( pulse( trig, echo, &distance ) )
			return distance;
		return -1 ;
}
