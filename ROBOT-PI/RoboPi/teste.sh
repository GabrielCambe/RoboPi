#!/bin/bash
if [ -z "$1" ]
	then
		echo "Diga o teste que quer executar! ( pwm, motor, sensor )"
else
	rm teste_$1
	make teste_$1
	while true ; do ./teste_$1 ; done
fi
