#include "/home/pi/Documents/RoboPi/include/sensores.h"
#define VEL_SOM_CM_uS_div2 0.017150
#define VEL_SOM_cm_microsec 0.0343

int pulso( int trig, int echo, float *distance ){
	long int ping = 0;
	long int pong = 0;
	*distance = 0;
 	long int timeout = 500000; // 0.5 seg.
	
	// Para se certificar que o TRIGGER não está ativado antes da medição.
	digitalWrite( trig, LOW );
	delay( 100 ); // 0.0001 seg.
	
	// Manda um pulso de 30 microsegundos no pino TRIGGER.
	digitalWrite( trig, HIGH );
	delayMicroseconds( 30 );
	digitalWrite( trig, LOW );
	
	long int tempo_inicial, tempo_final;
	tempo_inicial = micros(); // inicializando a contagem do tempo de resposta do pulso mandado.
	tempo_final = micros(); // a diferença de tempo entre essas duas instruções é insignificante.
    //tempo_final = tempo_inicial; //inicializando o tempo final com o mesmo numero que o tempo inicial.

	// Esperando pela resposta no pino ECHO ou pelo timeout.
	while ( digitalRead( echo ) == LOW && (tempo_final - tempo_inicial) < timeout ){
		tempo_final = micros();
	}
	// Cancela a medição no caso de timeout.
	if ( (tempo_final - tempo_inicial) > timeout ){
		printf("Fora de Alcance.\n"); return 0 ;
	}

	ping = micros(); // Aqui começamos a receber o pulso de retorno no pino ECHO
	
	tempo_inicial = micros();
	tempo_final = micros();
    //tempo_final = tempo_inicial;

	// Esperando o pulso recebido acabar ou o timeout.
	//while ( digitalRead( echo ) == HIGH && (tempo_final - tempo_inicial) < timeout ){}
	while ( digitalRead( echo ) == HIGH && (tempo_final - tempo_inicial) < timeout ){
		tempo_final = micros();
	}
    // Cancela a medição no caso de timeout.
	if ( (tempo_final - tempo_inicial) > timeout ){
		printf("Fora de Alcance.\n"); return 0 ;
	}
	
	pong = micros(); // Aqui acabamos de receber o pulso de retorno no pino ECHO
	
	// Convertendo a duração do pulso em centimetros.
	*distance = (float) (pong - ping) * VEL_SOM_cm_microsec/2;

	printf( "Distance: %.2f cm.\n", *distance );
	
	return 1;
}

float distancia( int trig, int echo ){
	float distance;
	if ( pulso( trig, echo, &distance ) )
		return distance ;
	else
		return -1 ;
}
