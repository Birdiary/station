import sys
import time
import schedule
import numpy as np
from datetime import datetime, timedelta 
import os 
import requests
import yaml
import json

print("Start setup!") 

# Read config.yaml file
print("Reading configuration file!")
with open("/home/pi/station/config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)
    
serverUrl = yamlData["server"]["url"]
boxId = yamlData["station"]["boxId"]
environmentTimeDeltaInMinutes = yamlData["station"]["environmentTimeDeltaInMinutes"] # waiting time to send environment requests 
weightThreshold = yamlData["station"]["weightThreshold"] # weight which is the threshold to recognize a movement 
balanceReferenceUnit = yamlData["station"]["balanceReferenceUnit"] # reference unit for the balance

# Setup Camera 
print("Setup camera!")
import io
import random
import picamera

camera = picamera.PiCamera()
camera.rotation = 180
camera.resolution = (1280, 960)
stream = picamera.PiCameraCircularIO(camera, seconds=5)
camera.start_recording(stream, format='h264')

# Setup DHT22 (humidity + temperature) 
print("Setup DHT22!")
import adafruit_dht
from board import *
SENSOR_PIN = D16 # use not board but GPIO number 
dht22 = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)

# Setup Balance
print("Setup balance!")
EMULATE_HX711=False

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from balance.hx711 import HX711
else:
    from balance.emulated_hx711 import HX711

hx = HX711(17, 23)

hx.set_reading_format("MSB", "MSB")
# readValueTerminal/referenceValueOnBalance=referenceUnit e.g. -1020389.3333333334/1000 = -1020,389
hx.set_reference_unit(balanceReferenceUnit)

hx.power_up()
hx.reset()
hx.tare()

# Setup Microphone 
print("Setup microphone!")
from audio import record
import threading 

#recorder = threading.Thread(target=record, args=(duration, path))

print("Setup finished!") 

# Function to send environment data to the server
def send_environment(environment_data, box_id):
    
    r = requests.post(serverUrl + "environment/" + box_id, json=environment_data)
    print("Environment Data send with the corresponding environment_id: ")
    print(r.content)

# Function to send a movement to the server 
def send_movement(files, box_id):
    
    r = requests.post(serverUrl + "movement/" + box_id, files=files)
    print("Movement Data send with the corresponding movement_id: ")
    print(r.content)

# Function to track a environment  
def track_environment(): 
   print("Collect Environment Data") 
   environment = {}
   environment["date"] = str(datetime.now())
   environment["temperature"] = dht22.temperature
   environment["humidity"] = dht22.humidity
   
   print("Environment Data: ")
   print(environment)
                 
   send_environment(environment, boxId)
    
   global environmentData 
   environmentData = environment 

# predefined variables 
environmentData = None 

# Function to track a movement      
def track_movement(): 
   values = [] 
   
   # schedule an environment track for every x minutes    
   schedule.every(environmentTimeDeltaInMinutes).minutes.do(track_environment)

   while True:
       try:
           schedule.run_pending()
           
           weight = hx.get_weight(17)  
           
           if (weight < weightThreshold  and len(values) == 0):
              print("Waiting for movement! (currently measured weight: " + str(weight) + ")")
           
           # start movement if weight higher than threshold is recognized 
           if (weight > weightThreshold and len(values) == 0):
              print("Movement recognized!") 
              
              recorder = threading.Thread(target=record, args=(3, '/home/pi/station/files'))
              recorder.start()
              
              movementStartDate = datetime.now()
              
              camera.wait_recording(1) # continue camera recording 
            
              values.append(weight) # add current weight to weight list 
              
              # if recorder.is_alive():
                 # recorder.join()
                 # print("joined recorder")
              # if not recorder.is_alive():
                 # print(str(recorder.is_alive()))
                 # recorder.start()
              # else: 
                 # print("recorder not started")
                         
           else: 
           # continue movement if currently recognized weight is above threshold 
              if (weight > weightThreshold):
                 values.append(weight)
                 camera.wait_recording(1)

                 print("Currently measured weight: " + str(weight))

        
           hx.power_down()
           hx.power_up()           
        
           # stop movement if weight is below threshold 
           if (weight < weightThreshold):
              if (len(values) >= 1):
                 print("Movement ending!") 
                 movementEndDate = datetime.now() 
                 
                 duration = (movementEndDate - movementStartDate).total_seconds()                 
                 stream.copy_to('/home/pi/station/files/' + str(movementStartDate) + '.h264', seconds=duration+5)
                 stream.clear()
                                  
                 movementData = {}
                 files = {}
                 movementData["start_date"] = str(movementStartDate)
                 movementData["end_date"] = str(movementEndDate)
                 movementData["audio"] = "audioKey"
                 movementData["weight"] = np.median(values)
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
                 
                 print("Movement Data: ")
                 print(movementData)
                 
                 files["json"] = (None, json.dumps(movementData), 'application/json')

                 send_movement(files, boxId)
                 
                 values = []
                 os.remove('/home/pi/station/files/sound.wav')
                 os.remove('/home/pi/station/files/' + str(movementStartDate) + '.h264')
                 
       except (KeyboardInterrupt, SystemExit):
           cleanAndExit()
        
print("Start Birdiary!")
track_movement() 








