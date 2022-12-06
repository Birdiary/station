#!/bin/bash
echo "Welcome to Birdiary!" 

cd /home/pi/station
python3 main.py &
ONLINE=1

while true; do
  sleep 60
  echo "Internet Test!"
  ping -q -c 1 -w 1 www.google.com >/dev/null 2>&1
  ONLINE=$?
  echo $ONLINE
  if [ $ONLINE != 0 ]
       then
         sudo ip link set wlan0 down
         echo "Stop Internet Connection!" 
         sleep 5
         echo "Restart Internet Connection!" 
         sudo ip link set wlan0 up
     fi
  if [ $ONLINE == 0 ]
       then
          echo "Internet Connection is working"
     fi
done
exit
