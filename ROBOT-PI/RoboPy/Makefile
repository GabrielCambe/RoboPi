.PHONY: clean

clean:
	@rm -rf *~ || true
	@rm -rf control.py_* || true
	@ls

list_csv:
	@ls control.py_* -Ss1pq --block-size=1
	
count:
	@ls control.py_* | wc -l

copy_csv:
	scp pi@192.168.1.100:/home/pi/Documents/ROBOT-PI/RoboPy/control.py_* .

deploy:
	scp -r controle-experimento/ pi@192.168.1.100:/home/pi/Documents/ROBOT-PI/RoboPy