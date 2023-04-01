#!/bin/bash
echo "Welcome to Birdiary!" 


cd ~/station
until python3 main.py
do
    echo "Restarting"
    sleep 2
done 


exit
