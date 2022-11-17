#!/usr/bin/env python3
"""Send all data to the server if internet connection is up

"""
import requests
import glob
import yaml
import json
import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler
import schedule
import time

logname = "logs/send.log"
file_handler = TimedRotatingFileHandler(logname, when="midnight", interval=1)
file_handler.suffix = "%Y%m%d"

""" # Block just works for Python version >= 3.9
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
sendTimeDeltaInMinutes = yamlData["station"]["sendTimeDeltaInMinutes"]

logging.info('loglevel=' + str(loglevel))
logging.info('dev_mode=' + str(dev_mode))
logging.info('sendTimeDeltaInMinutes=' + str(sendTimeDeltaInMinutes))

# Function to send environment data to the server
def send_environment(filename, server_url, box_id):
	with open(filename, 'r') as envFile:
		data = json.load(envFile)
		
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
	with open(data_filename, 'r') as dataFile:
		data = json.load(dataFile)
	
	files = {}
	files['videoKey'] = (os.path.basename(video_filename), open(video_filename, 'rb'))
	files['audioKey'] = (os.path.basename(audio_filename), open(audio_filename, 'rb'))
	files['json'] = (None, json.dumps(data), 'application/json')
		
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
	logging.info('Starting job')
	environmentFiles = sorted(glob.glob('environments/*.json'))
	videoFiles = sorted(glob.glob('movements/*.h264'))
	audioFiles = sorted(glob.glob('movements/*.wav'))
	dataFiles = sorted(glob.glob('movements/*.json'))	

	for file in environmentFiles:
		send_environment(file, serverUrl, boxId)
	for (video, audio, data) in zip(videoFiles, audioFiles, dataFiles):
		send_movement(video, audio, data, serverUrl, boxId)
	logging.info('Job done. Returning in one hour.')

schedule.every(sendTimeDeltaInMinutes).minutes.do(send_data)

schedule.run_all()
while True:
	schedule.run_pending()
	time.sleep(30)
