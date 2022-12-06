#!/usr/bin/env python3
"""Send all data to the server if internet connection is up

"""
import requests
import glob
import yaml
import json
import sys
import os

import time


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
# Read config.yaml file
logging.info("Reading configuration file!")
with open("config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)





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
	videoFiles = sorted(glob.glob('savedMovements/*.h264'))
	audioFiles = sorted(glob.glob('savedMovements/*.wav'))
	dataFiles = sorted(glob.glob('savedMovements/*.json'))	

	for file in environmentFiles:
		send_environment(file, serverUrl, boxId)
	for (video, audio, data) in zip(videoFiles, audioFiles, dataFiles):
		send_movement(video, audio, data, serverUrl, boxId)
	logging.info('Job done. Returning in one hour.')

