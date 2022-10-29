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

dev_mode = False

logname = "logs/send.log"
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

# Read config.yaml file
logging.info("Reading configuration file!")
with open("config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)
    
serverUrl = yamlData["server"]["url"]
boxId = yamlData["station"]["boxId"]

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
			logging.info('Following environment data send:')
			logging.info(data)
			logging.info('Corresponding environment_id:')
			logging.info(r.content)
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
			logging.info('Following movement data send:')
			logging.info(files)
			logging.info('Corresponding movement_id:')
			logging.info(r.content)
		except (requests.ConnectionError, requests.Timeout) as exception:
			logging.warning('No internet connection. ' + str(exception))
		else:
			os.remove(video_filename)
			os.remove(audio_filename)
			os.remove(data_filename)

def send_data():
	logging.info('Starting job')
	environmentFiles = sorted(glob.glob('environments/*.json'))
	videoFiles = sorted(glob.glob('files/*.h264'))
	audioFiles = sorted(glob.glob('files/*.wav'))
	dataFiles = sorted(glob.glob('files/*.json'))	

	for file in environmentFiles:
		send_environment(file, serverUrl, boxId)
	for (video, audio, data) in zip(videoFiles, audioFiles, dataFiles):
		send_movement(video, audio, data, serverUrl, boxId)
	logging.info('Job done. Returning in one hour.')

schedule.every(20).minutes.do(send_data)

schedule.run_all()
while True:
	schedule.run_pending()
	time.sleep(60)
