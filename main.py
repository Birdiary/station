import sys
import shutil
import time
import schedule
import numpy as np
from datetime import datetime, timedelta 
import os 
import yaml
import json
import logging
from logging.handlers import TimedRotatingFileHandler

dev_mode = False
if not dev_mode:
    import requests

if not os.path.exists('files'):
    os.makedirs('files')
if not os.path.exists('logs'):
    os.makedirs('logs')
if not os.path.exists('environments'):
    os.makedirs('environments')
if not os.path.exists('temp'):
    os.makedirs('temp')

logname = "logs/birdiary.log"
file_handler = TimedRotatingFileHandler(logname, when="midnight", interval=1)
file_handler.suffix = "%Y%m%d"

logging.basicConfig(encoding='utf-8', 
                    level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s',
                    handlers=[
                      file_handler,
                      logging.StreamHandler(sys.stdout)
                    ]
)
logger = logging.getLogger()

logging.info("Start setup!") 

# Read config.yaml file
logging.info("Reading configuration file!")
with open("config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)
    
# parse loglevel if present
try:  # make it backward compatible to older Versions
    loglevel = yamlData["misc"]["loglevel"]
    if loglevel == 0 or loglevel == 10 or loglevel == 20 or loglevel == 30 or loglevel == 40 or loglevel == 50:
        # referring to https://docs.python.org/3/library/logging.html#logging-levels
        logger.setLevel(loglevel)
    else:
        logger.error("Loglevel in configuration file wrong")
except:
    logger.error("loglevel in configuration not set")

# parse dev_mode if present
try:  # make it backward compatible to older Versions
    dev_mode = yamlData["misc"]["dev_mode"]
except:
    dev_mode = False
    logger.error("dev_mode in configuration not set, disabled by default")

serverUrl = yamlData["server"]["url"]
boxId = yamlData["station"]["boxId"]
environmentTimeDeltaInMinutes = yamlData["station"]["environmentTimeDeltaInMinutes"] # waiting time to send environment requests 
weightThreshold = yamlData["station"]["weightThreshold"] # weight which is the threshold to recognize a movement 
terminal_weight = yamlData["station"]["terminal_weight"] # reference unit for the balance
calibration_weight = yamlData["station"]["calibration_weight"] # reference unit for the balance

logging.info('loglevel=' + str(loglevel))
logging.info('dev_mode=' + str(dev_mode))
logging.info('environmentTimeDeltaInMinutes=' + str(environmentTimeDeltaInMinutes))

# Setup Camera 
logging.info("Setup camera!")
import io
import random
import picamera

camera = picamera.PiCamera()
camera.rotation = 180
camera.resolution = (1280, 960)
stream = picamera.PiCameraCircularIO(camera, seconds=5)
camera.start_recording(stream, format='h264')

# Setup DHT22 (humidity + temperature) 
logging.info("Setup DHT22!")
import adafruit_dht
from board import *
SENSOR_PIN = D16 # use not board but GPIO number 
dht22 = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)

# Setup Balance
logging.info("Setup balance!")
EMULATE_HX711=False

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from balance.hx711 import HX711
else:
    from balance.emulated_hx711 import HX711

hx = HX711(17, 23)

hx.set_reading_format("MSB", "MSB")
# readValueTerminal/referenceValueOnBalance=referenceUnit e.g. -1020389.3333333334/1000 = -1020,389

if calibration_weight != 0:
    balanceReferenceUnit = terminal_weight/calibration_weight
    hx.set_reference_unit(balanceReferenceUnit)

hx.power_up()
hx.reset()
hx.tare()

# Setup Microphone 
logging.info("Setup microphone!")
from rec_unlimited import record
from multiprocessing import Process

logging.info("Setup finished!") 
 
def write_environment(environment_data):
    filename = 'environments/' + environment_data['date'] + '.json'
    with open(filename, 'w') as wfile:
        json.dump(environment_data, wfile)

# Function to track a environment  
def track_environment(): 
   try:
      logging.info("Collect Environment Data") 
      environment = {}
      environment["date"] = str(datetime.now())
      environment["temperature"] = dht22.temperature
      environment["humidity"] = dht22.humidity
      
      logging.info("Environment Data: ")
      logging.info(environment)
                  
      write_environment(environment)
      
      global environmentData 
      environmentData = environment 
   except Exception as e:
      logging.error(e)  

# predefined variables 
environmentData = None
audio_filename = None
video_filename = None
temp_audio_filename = 'temp/audio.wav'
data_filename = None
recorder = None

def set_filenames(movementStartDate):
    global audio_filename
    audio_filename = 'files/' + str(movementStartDate) + '.wav'
    global video_filename
    video_filename = 'files/' + str(movementStartDate) + '.h264'
    global data_filename
    data_filename = 'files/' + str(movementStartDate) + '.json'

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
              logging.info("Waiting for movement! (currently measured weight: " + str(weight) + ")")
           
           # start movement if weight higher than threshold is recognized 
           if (weight > weightThreshold and len(values) == 0):
              logging.info("Movement recognized!") 
              movementStartDate = datetime.now()
              set_filenames(movementStartDate)
              
              global recorder
              recorder = Process(target=record, args=(temp_audio_filename,))
              recorder.start()
              
              camera.wait_recording(1) # continue camera recording 
            
              values.append(weight) # add current weight to weight list 

           else: 
           # continue movement if currently recognized weight is above threshold 
              if (weight > weightThreshold):
                 values.append(weight)
                 camera.wait_recording(1)

                 logging.info("Currently measured weight: " + str(weight))

           hx.reset()          
        
           # stop movement if weight is below threshold 
           if (weight < weightThreshold):
              if (len(values) >= 1):
                 logging.info("Movement ending!") 
                 movementEndDate = datetime.now() 
                 
                 duration = (movementEndDate - movementStartDate).total_seconds()                 
                 stream.copy_to(video_filename, seconds=duration+5)
                 stream.clear()
                                                   
                 movementData = {}
                 files = {}
                 movementData["start_date"] = str(movementStartDate)
                 movementData["end_date"] = str(movementEndDate)
                 movementData["audio"] = "audioKey"
                 movementData["weight"] = np.median(values)
                 movementData["video"] = "videoKey"
                 
                 # stop audio recording and move temporary file to output directory 
                 terminate_recorder()
                 shutil.move(temp_audio_filename, audio_filename)
                 
                 files['audioKey'] = (os.path.basename(audio_filename), open(audio_filename, 'rb'))
                 files['videoKey'] = (os.path.basename(video_filename), open(video_filename, 'rb'))

                 
                 if (environmentData != None):
                    movementData["environment"] = environmentData
                 else: 
                    movementData["environment"] = {}
                 
                 logging.info("Movement Data: ")
                 logging.info(movementData)
                 
                 files["json"] = (None, json.dumps(movementData), 'application/json')

                 with open(data_filename, 'w') as jsonfile:
                    jsonfile.write(files['json'][1])
                 
                 values = []
                 
       except (KeyboardInterrupt, SystemExit):
           cleanAndExit()
           
def cleanAndExit():
  camera.close()
  terminate_recorder()
  sys.exit(0)
  
def terminate_recorder():
  global recorder
  if recorder.is_alive():
    recorder.terminate()
    logging.info("terminated recorder")
  else:
    logging.debug("no alive recorder")
        
logging.info("Start Birdiary!")
track_movement() 








