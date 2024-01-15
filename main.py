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
import glob
import requests



dev_mode = False
if not dev_mode:
    import requests

if not os.path.exists('files'):
    os.makedirs('files')
if not os.path.exists('logs'):
    os.makedirs('logs')
if not os.path.exists('environments'):
    os.makedirs('environments')
if not os.path.exists('movements'):
    os.makedirs('movements')
else: 
    files = glob.glob('movements/*')
    for f in files:
        os.remove(f)
if not os.path.exists('savedMovements'):
    os.makedirs('savedMovements')
if not os.path.exists('temp'):
    os.makedirs('temp')
if os.path.exists('temp/audio.raw'):
    os.remove('temp/audio.raw')
logname = "logs/birdiary.log"
file_handler = TimedRotatingFileHandler(logname, when="midnight", interval=1)
file_handler.suffix = "%Y%m%d"

""" # This block just works for Python version >= 3.9
logging.basicConfig(encoding='utf-8', 
                    level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s',
                    handlers=[
                      file_handler,
                      logging.StreamHandler(sys.stdout)
                    ]
) 
"""
logger = logging.getLogger()

logger.setLevel(logging.DEBUG)  
logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler(sys.stdout))


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
camera_rotation =  yamlData["station"]["cameraRotation"]
weightResetInMinutes = yamlData["station"]["weightResetInMinutes"]

logging.info('loglevel=' + str(loglevel))
logging.info('dev_mode=' + str(dev_mode))
logging.info('environmentTimeDeltaInMinutes=' + str(environmentTimeDeltaInMinutes))

# Setup Camera 
logging.info("Setup camera!")
import io
import random
import picamera

camera = picamera.PiCamera()
camera.rotation = camera_rotation
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
time.sleep(30)
hx.tare()

# Setup Microphone 
logging.info("Setup microphone!")
from rec_unlimited import record
from multiprocessing import Process
from pydub import AudioSegment  # for converting the raw to mp3
audio_gain = yamlData["station"]["audio_gain"]
logging.info("Setup finished!") 
 
def write_environment(environment_data):
    filename = 'environments/' + environment_data['date'] + '.json'
    with open(filename, 'w') as wfile:
        json.dump(environment_data, wfile)

def write_movement(movement_data):
    with open(data_filename, 'w') as jsonfile:
        jsonfile.write(movement_data)

# Function to send movement data to the server
def send_realtime_movement(files):
        
    if dev_mode:
        logging.warning('send_movement deactivated')
        logging.warning('received: ' + str(video_filename) + ' ' + str(audio_filename) + ' ' + str(data_filename))
    else:
        try:
            logging.debug(serverUrl + 'movement/' + boxId)
            r = requests.post(serverUrl + 'movement/' + boxId, files=files, timeout=60)
            logging.info('Following movement data send: %s', files)
            logging.debug('Corresponding movement_id: %s', r.content)
        except (requests.ConnectionError, requests.Timeout) as exception:
            logging.warning('No internet connection. ' + str(exception))
            logging.warning('Saving files to send later')
            shutil.move(audio_filename, save_audio_filename)
            shutil.move(video_filename, save_video_filename)
            write_movement(files['json'][1])
        else:
            os.remove(video_filename)
            os.remove(audio_filename)

def send_realtime_environment(environmentData):
    if dev_mode:
        logging.warning('send_environment deactivated')
        logging.warning('received: ' + str(environmentData))
    else:
        try:
            r = requests.post(serverUrl + 'environment/' + boxId, json=environmentData, timeout=20)
            logging.info('Following environment data send: %s', environmentData)
            logging.debug('Corresponding environment_id: %s', r.content)
        except (requests.ConnectionError, requests.Timeout) as exception:
            logging.warning('No internet connection. ' + str(exception))
            logging.warning("Saving environment data to send later")
            write_environment(environmentData)
        else:
            send_data()            

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
                  
      send_realtime_environment(environment)
      
      global environmentData 
      environmentData = environment 
    except Exception as e:
      logging.error(e)  

# predefined variables 
environmentData = None
audio_filename = None
video_filename = None
save_audio_filename = None
save_video_filename = None
temp_audio_filename = 'temp/audio.raw'  # the filename extension has to be .raw to convert it later to mp3
data_filename = None
recorder = None

def tare():
    weight2 = hx.get_weight(15)
    if(weight2<weightThreshold):
        while((weight2 < -0.5 or weight2>0.5)):
            logging.info("Measured weight:" + str(weight2) + " not in valid range. Start taring")
            hx.tare()
            time.sleep(5)
            weight2 = hx.get_weight(15)
    logging.info("Measured weight:" + str(weight2) + " in valid range. Stop taring")
            



def set_filenames(movementStartDate):
    global save_audio_filename
    save_audio_filename = 'savedMovements/' + str(movementStartDate) + '.wav'
    global save_video_filename
    save_video_filename = 'savedMovements/' + str(movementStartDate) + '.h264'
    global audio_filename
    audio_filename = 'movements/' + str(movementStartDate) + '.mp3'
    global video_filename
    video_filename = 'movements/' + str(movementStartDate) + '.h264'
    global data_filename
    data_filename = 'savedMovements/' + str(movementStartDate) + '.json'

# Function to track a movement      
def track_movement(): 
   values = []

   

   
   # schedule an environment track for every x minutes    
   schedule.every(environmentTimeDeltaInMinutes).minutes.do(track_environment)
   schedule.every(weightResetInMinutes).minutes.do(tare)



   while True:
       try:
           schedule.run_pending()
           
           weight = hx.get_weight(15)  
           
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
                 tags_json = dict(title=(movementStartDate.strftime("%Y-%M-%d %H:%m:%S") + '_' + boxId),
                                  track=1, artist=boxId,
                                  copyright='www.wiediversistmeingarten.org',
                                  genre="Noise", date=movementStartDate.strftime("%Y-%M-%d"))
                 RawAudio = AudioSegment.from_raw(temp_audio_filename, sample_width=2, frame_rate=48000, channels=1)
                 RawAudioVolumeLifted = RawAudio.apply_gain(audio_gain)  # lift up the volume
                 RawAudioVolumeLifted.export(audio_filename, format='mp3', tags=tags_json, id3v2_version="3")
                 os.remove(temp_audio_filename)
                 # shutil.move(temp_audio_filename, audio_filename)
                 
                 files['audioKey'] = (os.path.basename(audio_filename), open(audio_filename, 'rb'))
                 files['videoKey'] = (os.path.basename(video_filename), open(video_filename, 'rb'))

                 
                 if (environmentData != None):
                    movementData["environment"] = environmentData
                 else: 
                    movementData["environment"] = {}
                 
                 logging.info("Movement Data: ")
                 logging.info(movementData)
                 
                 files["json"] = (None, json.dumps(movementData), 'application/json')

                 send_realtime_movement(files)
                 
                 values = []

                 
       except (KeyboardInterrupt, SystemExit):
           cleanAndExit()
           
def cleanAndExit():
  camera.close()
  terminate_recorder()
  sys.exit(2)
  
def terminate_recorder():
  global recorder
  if recorder is not None and recorder.is_alive():
    recorder.terminate()
    logging.info("terminated recorder")
  else:
    logging.debug("no alive recorder")
    
#Function to send environment data to the server
def send_environment(filename, server_url, box_id):
	try:
		with open(filename, 'r') as envFile:
			data = json.load(envFile)
	except:
		os.remove(filename)
		
	if dev_mode:
		logging.warning('send_environment deactivated')
		logging.warning('received: ' + str(data))
	else:
		try:
			r = requests.post(server_url + 'environment/' + box_id, json=data, timeout=20)
			logging.info('Following environment data send: %s', data)
			logging.debug('Corresponding environment_id: %s', r.content)
		except (requests.ConnectionError, requests.Timeout) as exception:
			logging.warning('No internet connection. ' + str(exception))
		else:
			os.remove(filename)
			
# Function to send movement data to the server
def send_movement(video_filename, audio_filename, data_filename, server_url, box_id):
	try: 
		with open(data_filename, 'r') as dataFile:
			data = json.load(dataFile)
		files = {}
		files['videoKey'] = (os.path.basename(video_filename), open(video_filename, 'rb'))
		files['audioKey'] = (os.path.basename(audio_filename), open(audio_filename, 'rb'))
		files['json'] = (None, json.dumps(data), 'application/json')
	except:
		os.remove(video_filename)
		os.remove(audio_filename)
		os.remove(data_filename)
		

		
	if dev_mode:
		logging.warning('send_movement deactivated')
		logging.warning('received: ' + str(video_filename) + ' ' + str(audio_filename) + ' ' + str(data_filename))
	else:
		try:
			logging.debug(serverUrl + 'movement/' + box_id)
			r = requests.post(serverUrl + 'movement/' + box_id, files=files, timeout=60)
			logging.info('Following movement data send: %s', files)
			logging.debug('Corresponding movement_id: %s', r.content)
		except (requests.ConnectionError, requests.Timeout) as exception:
			logging.warning('No internet connection. ' + str(exception))
		else:
			os.remove(video_filename)
			os.remove(audio_filename)
			os.remove(data_filename)

def send_data():
	logging.info('Sending stored data')
	environmentFiles = sorted(glob.glob('environments/*.json'))
	videoFiles = sorted(glob.glob('savedMovements/*.h264'))
	audioFiles = sorted(glob.glob('savedMovements/*.wav'))
	dataFiles = sorted(glob.glob('savedMovements/*.json'))	

	for file in environmentFiles:
		send_environment(file, serverUrl, boxId)
	for (video, audio, data) in zip(videoFiles, audioFiles, dataFiles):
		send_movement(video, audio, data, serverUrl, boxId)
	logging.info('All stored data send!')
        
logging.info("Start Birdiary!")
track_movement() 








