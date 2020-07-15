#!/bin/bash
for i in $(seq 1 $1); do
    echo python3 gerar-log.py $i
    python3 gerar-log.py $i
done