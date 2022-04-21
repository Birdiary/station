import sys
import time
import schedule
import numpy as np
from datetime import datetime, timedelta 
import os 
import requests
import yaml
import json

# Read config.yaml file
with open("/home/pi/station/config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)
    
serverUrl = yamlData["server"]["url"]
boxId = yamlData["station"]["boxId"]
environmentTimeDeltaInMinutes = yamlData["station"]["environmentTimeDeltaInMinutes"] # waiting time to send environment requests 

# setup camera 
from picamera import PiCamera 
camera = PiCamera()
camera.rotation = 180
camera.resolution = (1280, 960)
#camera.resolution = (640, 480)

# setup DHT22 
# (humidity + temperature) needed import: "sudo pip3 install adafruit-circuitpython-dht"
import adafruit_dht
from board import *
SENSOR_PIN = D16 # use not board but GPIO number 
dht22 = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)

# setup balance
EMULATE_HX711=False

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from balance.hx711 import HX711
else:
    from balance.emulated_hx711 import HX711

hx = HX711(17, 23)

hx.set_reading_format("MSB", "MSB")
# hx.set_reference_unit(-1093) # -295000/270 = -1093
# -1020389.3333333334/1000 = -1020,389
hx.set_reference_unit(-1020.389)
print ("Balance Setup done")

# Add sensor values to detection   
# Add weight 
hx.power_up()
hx.reset()
hx.tare()

# setup recording 
from audio import record
import threading 

#duration = 3
#path = '/home/pi/station/files'

#recorder = threading.Thread(target=record, args=(duration, path))


# function to send environment data to the server
def send_environment(environment_data, box_id):
    
    r = requests.post(serverUrl + "environment/" + box_id, json=environment_data)
    print("environment_id:")
    print(r.content)

# function to send a movement to the server 
def send_movement(files, box_id):
    
    r = requests.post(serverUrl + "movement/" + box_id, files=files)
    print("movement_id:")
    print(r.content)

# function to track a movement 
def track_environment(): 
   print("collect environmentData") 
   environment = {}
   environment["date"] = str(datetime.now())
   environment["temperature"] = dht22.temperature
   environment["humidity"] = dht22.humidity
   
   send_environment(environment, boxId)
    
   global environmentData 
   environmentData = environment 


environmentData = None 
     
def track_movement(): 
   values = [] 
      
   schedule.every(2).minutes.do(track_environment)

   while True:
       try:
           schedule.run_pending()

           print("hi")
           
           weight = hx.get_weight(17)  

           print(weight)
           
           # start movement 
           if (weight > 5 and len(values) == 0):
              print("movement recognized") 
              recorder = threading.Thread(target=record, args=(3, '/home/pi/station/files'))
              recorder.start()
              movementStartDate = datetime.now()
              camera.start_recording('/home/pi/station/files/' + str(movementStartDate) + '.h264')
              values.append(weight)
              # if recorder.is_alive():
                 # recorder.join()
                 # print("joined recorder")
              # if not recorder.is_alive():
                 # print(str(recorder.is_alive()))
                 # recorder.start()
              # else: 
                 # print("recorder not started")
                         
           else: 
           # continue movement 
              if (weight > 5):
                 values.append(weight)
        
           print(values) 
           hx.power_down()
           hx.power_up()
           time.sleep(0.1)
           
        
           # stop movement 
           if (weight < 5):
              if (len(values) >= 1):
                 print("movement ending") 
                 camera.stop_recording()
                 movementEndDate = datetime.now() 
                 print(values) 
                 print(np.median(values))
                 
                 movementData = {}
                 files = {}
                 movementData["start_date"] = str(movementStartDate)
                 movementData["end_date"] = str(movementEndDate)
                 movementData["audio"] = "audioKey"
                 movementData["weight"] = str(np.median(values))
                 movementData["video"] = "videoKey"
                 
                 try:
                    if recorder.is_alive():
                       recorder.join()
                       print("terminated recorder")
                 except: 
                    print("no alive recorder")
                    
                 files['audioKey'] = (os.path.basename("/home/pi/station/files/sound.wav"), open("/home/pi/station/files/sound.wav", 'rb'))
                 files['videoKey'] = (os.path.basename('/home/pi/station/files/' + str(movementStartDate) + '.h264'), open('/home/pi/station/files/' + str(movementStartDate) + '.h264', 'rb'))

                 
                 if (environmentData != None):
                    movementData["environment"] = environmentData

                 else: 
                    movementData["environment"] = {}
                 
                 print(movementData)
                 
                 files["json"] = (None, json.dumps(movementData), 'application/json')

                 send_movement(files, boxId)
                 
                 values = []
                 os.remove('/home/pi/station/files/sound.wav')
                 os.remove('/home/pi/station/files/' + str(movementStartDate) + '.h264')

       except (KeyboardInterrupt, SystemExit):
           cleanAndExit()
        
print("Start Birdiary")
track_movement() 








