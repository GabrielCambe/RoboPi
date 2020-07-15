#!/bin/bash
raw_data=$(cat $1)

touch sensrF.dat
touch sensrE.dat
touch sensrD.dat

for linha in $raw_data; do
    echo $linha | awk -F, '{print $1" " $2" " $3}' >> sensrF.dat
    echo $linha | awk -F, '{print $1" " $2" " $4}' >> sensrD.dat
    echo $linha | awk -F, '{print $1" " $2" " $5}' >> sensrE.dat
done

gnuplot -c "plot.gplt" "sensrF.dat" "sensrD.dat" "sensrE.dat"
