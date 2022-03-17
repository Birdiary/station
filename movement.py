#!/usr/bin/python
 
#Import
import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta 
from picamera import PiCamera 
import os 
import shutil
import json
import requests
import yaml

# DHT22 (humidity + temperature) needed import: "sudo pip3 install adafruit-circuitpython-dht"
import adafruit_dht
from board import *

# Read config.yaml file
with open("/home/pi/station/config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)
    
serverUrl = yamlData["server"]["url"]
boxId = yamlData["station"]["boxId"]
environmentTimeDeltaInMinutes = yamlData["station"]["environmentTimeDeltaInMinutes"] # waiting time to send environment requests 

#def post_box():
#   payload = { 
#            "name": "Peter Lustigs Station",
#            "location": {
#               "lat": 51.399206,
#               "lon": 9.688879
#               },
#            "mail": {"adresses": ["xxx.xxx@countyourbirds.org"]}
#            }
#            
#   r = requests.post("http://10.14.29.24:5000/box", json=payload)
#   print(r.content)


# raw json variable for the environment data 
environment_data = {}
#environment_data = {"date": None, "temp": None}

# raw json variable for the movement data 
movement_data = {}
#movement_data = {
#        "start_date" : None,
#        "end_date" : None,
#        "audio" : None,
#        "environment" : {
#            "date": None,
#            "temp": None
#        },
#        "detections" : [None]
#}

# raw json variable for the files which get send with the movement request 
files = {}

# function to send environment data to the server
def send_environment(environment_data, box_id):
    
    r = requests.post(serverUrl + "/environment/" + box_id, json=environment_data)
    print("environment_id:")
    print(r.content)

# function to send a movement to the server 
def send_movement(files, box_id):
    
    
    r = requests.post(serverUrl + "/movement/" + box_id, files=files)
    print("movement_id:")
    print(r.content)



print ("CountYourBirds Start")



# Setup balance  
import sys
EMULATE_HX711=False

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from balance.hx711 import HX711
else:
    from balance.emulated_hx711 import HX711

hx = HX711(17, 18)

hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(-1093) # -295000/270 = -1093
print ("Balance Setup done")





#Setup DHT22 
SENSOR_PIN = D16 # use not board but GPIO number 
dht22 = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)
  
#Setup motion sensor 
GPIO.setmode(GPIO.BCM)
 
PIR_GPIO = 23 # use not board but GPIO number 
GPIO.setup(PIR_GPIO,GPIO.IN)

# counting variables
read=0 # read=1 system is currently detecting a movement 
wait=0 # wait=1 system is waiting for a movement 
sleepCounter=0 # variable to indicate how long a movement takes  
detectionCounter = 0 # counter to count different detections during a movement

# further needed variables 
mainPath = './movements/' # path to store detections with images 
now_plus_environment_interval = datetime.now() + timedelta(seconds = 1) # waiting time for the first environment request 
triggerWaitingTime=0.1 # seconds the motion sensor is wating to proof if there is still movement 

# initialize camera 
camera = PiCamera()
camera.rotation = 180

try:  
 while GPIO.input(PIR_GPIO)==1:
   read=0
 print ("Waiting for Movement...")
 
 while True : 
   read = GPIO.input(PIR_GPIO)
   
   
   # if a movement is firstly recognized 
   if read==1 and wait==0: 
     print ("ALARM: Movement recognized at" + str(datetime.now())) 
     wait=1
     HILFSVARIABLE = 1
     
     movementStartDate = datetime.now()
     movementPath = mainPath + 'movement'

     # if there was a previous movement, corresponding data gets deleted
     if(os.path.isdir(movementPath)):
        shutil.rmtree(movementPath) # delete old movement folder 

     os.makedirs(movementPath)
     
     detectionPath = movementPath + '/detection0'
     os.makedirs(detectionPath)
    
     # raw json variable to collection all sensor data during a movement 
     detection_data = {}
     
     # Add sensor values to detection   
     # Add weight 
     hx.power_up()
     hx.reset()
     hx.tare()
      
     weight = hx.get_weight(17)   
     
     hx.power_down()
     
     detection_data[0] = {
         "date": str(movementStartDate),
         "weight": weight} 

     # add image 
     camera.capture(detectionPath + '/image.jpg')
     
     
   # if the movement is over and system starts to wait for new movement 
   elif read==0 and wait==1: 
     print ("Movement is over!") 
     wait=0
     sleepCounter=0
     detectionCounter=0 
     
     movementEndDate = datetime.now()
     
     # after movement is over detections are investigated for birds
     os.system('python3 /home/pi/station/birdDetection.py --modeldir=/home/pi/station/models/Sample_TF_Lite_Model --imagedir ' + mainPath +'/movement')
     
     # set movement_data
     movement_data["start_date"] = str(movementStartDate)
     movement_data["end_date"] = str(movementEndDate)
   
     movement_data["audio"] = "audioKey"
     movement_data["environment"] = environment_data # add latest environment_data
     movement_data["detections"] = []

     files['audioKey'] = (os.path.basename("/home/pi/9PBX76J-birds.mp3"), open("/home/pi/9PBX76J-birds.mp3", 'rb'))
     
     # Proof if movement folder with detections exists 
     # could be the case that it was deleted if there were no birds recognized on the images 
     if (os.path.isdir("./movements/movement") == True):
        detections = os.listdir("./movements/movement")

        # for each detection set data and imageKey in the files json 
        for i in detections: 
        
           detection = {
               "date": None,
               "image": None,
               "weight" : None}
        
           split = i.split("n")
           detectionNumber = split[1]
        
           files['imageKey' + str(detectionNumber)] = (os.path.basename("image.jpg"), open("./movements/movement/detection" + str(detectionNumber) + "/image.jpg", 'rb'))
                
           detection["image"] = 'imageKey' + str(detectionNumber) 
           detection["date"] = detection_data[int(detectionNumber)]["date"]
           detection["weight"] = detection_data[int(detectionNumber)]["weight"]
         
           movement_data["detections"].append(detection)
        
        files["json"] = (None, json.dumps(movement_data), 'application/json')
     
        # send movement request 
        send_movement(files, boxId)
        
        print("Movement was sent to the server.") 
     
     else:
        print("Movement was not sent to the server as no birds were recognized.")
   
   # if the system is waiting for new movement 
   elif read==0 and wait==0: 
      current_time = datetime.now()
      
      # every x minutes the enviroment data is send to the server 
      if current_time > now_plus_environment_interval: 
         
         now_plus_environment_interval = current_time + timedelta(minutes = environmentTimeDeltaInMinutes)
         
         # add environment sensor 
         environment_data["date"] = str(datetime.now())
         environment_data["temperature"] = dht22.temperature
         environment_data["humidity"] = dht22.humidity
         
         # environment request 
         send_environment(environment_data, boxId)


   # if there is currently a movement 
   elif read==1 and wait==1 and HILFSVARIABLE!=1:
      # Achtung hier nochmal prüfen ohne HILFSVARIABLE wird diese Schleife auch ausgeführt, wenn oben erste Schleife startet. 
      print ("Waiting for movement end for " + str(sleepCounter))
      sleepCounter+=triggerWaitingTime
      time.sleep(triggerWaitingTime)

      detectionCounter+=1
      
      detectionPath = movementPath + '/detection' + str(detectionCounter)
      os.makedirs(detectionPath)
      
      # Add sensor values to detection   
      date = str(datetime.now())
      
      # Add weight 
      hx.power_up()
      hx.reset()
      hx.tare()
      
      weight = hx.get_weight(17)               

      hx.power_down()
      
      detection_data[detectionCounter] = {
         "date": date,
         "weight": weight}      
     
      # Add image
      camera.capture(detectionPath + '/image.jpg')

     
 time.sleep(0.01)
 
except KeyboardInterrupt:
 print ("Beendet")
 GPIO.cleanup()
