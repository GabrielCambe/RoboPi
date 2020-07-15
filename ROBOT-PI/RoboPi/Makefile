NOME = controle
CFLAGS = -Wall -lwiringPi -lpthread
DebugFLAGS = $(CFLAGS) -g
ObjFLAGS = $(CFLAGS) -c
CC = gcc
SRC = ./src/
INC = ./include/

all: tras.o parar.o direita.o esquerda.o frente.o hcsr04.o
	$(CC) tras.o parar.o direita.o esquerda.o frente.o hcsr04.o controle.c $(CFLAGS) -o $(NOME)



teclado: tras.o parar.o direita.o esquerda.o frente.o hcsr04.o
	$(CC) tras.o parar.o direita.o esquerda.o frente.o hcsr04.o controle-teclado.c $(CFLAGS) -o $(NOME)


hcsr04.o:
	$(CC) $(SRC)hcsr04.c $(ObjFLAGS)
	

movePWM.o:
	$(CC) $(SRC)movePWM.c $(ObjFLAGS)

tras.o:
	$(CC) $(SRC)tras.c $(ObjFLAGS)

parar.o:
	$(CC) $(SRC)parar.c $(ObjFLAGS)

direita.o:
	$(CC) $(SRC)direita.c $(ObjFLAGS)

esquerda.o:
	$(CC) $(SRC)esquerda.c $(ObjFLAGS)

frente.o:
	$(CC) $(SRC)frente.c $(ObjFLAGS)

teste_motor: tras.o parar.o direita.o esquerda.o frente.o hcsr04.o
	$(CC) tras.o parar.o direita.o esquerda.o frente.o hcsr04.o teste-motor.c $(CFLAGS) -o teste_motor
	
teste_pwm: movePWM.o hcsr04.o
	$(CC) movePWM.o hcsr04.o teste-pwm.c $(CFLAGS) -o teste_pwm 


clean:
	rm tras.o || true
	rm parar.o || true
	rm direita.o || true
	rm esquerda.o || true
	rm frente.o || true
	rm hcsr04.o || true
	rm movePWM.o || true

dist-clean: clean
	rm controle || true
