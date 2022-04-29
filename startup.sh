#!/bin/bash
echo "Welcome to Birdiary!" 

cd /home/pi/station

ONLINE=1

while true; do
  sleep 15 
  while [ $ONLINE -ne 0 ]
  do
     ping -q -c 1 -w 1 www.google.com >/dev/null 2>&1
     ONLINE=$?
     echo "Internet Test!"
     if [ $ONLINE -ne 0 ]
       then
         sudo ip link set wlan0 down
         echo "Stop Internet Connection!" 
         sleep 5
         echo "Restart Internet Connection!" 
         sudo ip link set wlan0 up
         sleep 15 
     fi
  done
  echo "Internet connection is working!"
  python3 main.py &
  ONLINE=1
  wait $!
done
exit
