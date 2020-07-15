#!/bin/bash
pkill -f controle-calibration-concurrent-2.py
emacs ~/Documents/ROBOT-PI/RoboPy/calibration/controle-calibration-concurrent-2.py&
python ~/Documents/ROBOT-PI/RoboPy/calibration/controle-calibration-concurrent-2.py
