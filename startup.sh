#!/bin/bash
echo hello 

cd /home/pi/station

ONLINE=1
while [ $ONLINE -ne 0 ]
do
   ping -q -c 1 -w 1 www.google.com >/dev/null 2>&1
   ONLINE=$?
   if [ $ONLINE -ne 0 ]
     then
       sleep 5
   fi
done
echo "We are on line!"

while true; do
  python3 movement.py &
  wait $!
  sleep 10
done
exit
