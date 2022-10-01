import sys
import time
import logging
from logging.handlers import RotatingFileHandler
import schedule
import numpy as np
from datetime import datetime, timedelta
import os
import requests
import yaml
import json

sys.stderr = open('/home/pi/station/log/error.log', 'a+')
sys.stderr.write('#########New Logging Section ' + str(datetime.now()) + ' ############\n')

# Create and configure logger
loglevel = logging.INFO  # Default Logging level if nothing is set in the config.yaml
rotfilehandler = logging.handlers.RotatingFileHandler(
    filename="/home/pi/station/log/main.log",
    maxBytes=250 * 1024,
    backupCount=5)
LOG_FORMAT = "%(asctime)s %(levelname)s  %(module)s: %(message)s"  # set Logging Format
logging.basicConfig(level=loglevel, format=LOG_FORMAT, handlers=[rotfilehandler])
logger = logging.getLogger()

print("Start setup!")
logger.info("### Start setup! ###")
# Read config.yaml file
print("Reading configuration file!")
logger.info("Reading configuration file!")
with open("/home/pi/station/config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)
# get loglevel from configuration file

try:  # make it backward compatible to older Versions
    loglevel = yamlData["misc"]["loglevel"]
    if loglevel == 0 or loglevel == 10 or loglevel == 20 or loglevel == 30 or loglevel == 40 or loglevel == 50:
        # referring to https://docs.python.org/3/library/logging.html#logging-levels
        logger.setLevel(loglevel)
        logger.info("set Logging level to %s" % loglevel)
    else:
        logger.error("Loglevel in configuration file wrong")
except:
    logger.error("Loglevel in configuration not set")

serverUrl = yamlData["server"]["url"]
boxId = yamlData["station"]["boxId"]
environmentTimeDeltaInMinutes = yamlData["station"][
    "environmentTimeDeltaInMinutes"]  # waiting time to send environment requests
weightThreshold = yamlData["station"]["weightThreshold"]  # weight which is the threshold to recognize a movement
terminal_weight = yamlData["station"]["terminal_weight"]  # reference unit for the balance
calibration_weight = yamlData["station"]["calibration_weight"]  # reference unit for the balance

logger.debug('Configfile data: serverUrl: %s; boxId: %s; environmentTimeDeltaInMinutes: \
            %s; weightThreshold: %s; terminal_weight: %s ;calibration_weight: %s'
             % (serverUrl, boxId, environmentTimeDeltaInMinutes, weightThreshold, terminal_weight, calibration_weight))

# Setup Camera 
print("Setup camera!")
logger.info("Setup camera!")
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
logger.info("Setup DHT22!")
import adafruit_dht
from board import *

SENSOR_PIN = D16  # use not board but GPIO number
dht22 = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)

# Setup Balance
print("Setup balance!")
logger.info("Setup balance!")
EMULATE_HX711 = False

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from balance.hx711 import HX711
else:
    from balance.emulated_hx711 import HX711

hx = HX711(17, 23)

hx.set_reading_format("MSB", "MSB")
# readValueTerminal/referenceValueOnBalance=referenceUnit e.g. -1020389.3333333334/1000 = -1020,389

if calibration_weight != 0:
    balanceReferenceUnit = terminal_weight / calibration_weight
    hx.set_reference_unit(balanceReferenceUnit)

hx.power_up()
hx.reset()
hx.tare()

# Setup Microphone 
print("Setup microphone!")
logger.info('Setup microphone!')
from rec_unlimited import record
from multiprocessing import Process

soundPath = '/home/pi/station/files/sound.wav'
if os.path.exists(soundPath):
    os.remove(soundPath)
    print("Soundfile deleted")
    logger.info('Soundfile deleted')
else:
    print("There was no soundfile to delete")
    logger.info('There was no soundfile to delete')

print("Setup finished!")
logger.info('### Setup finished! ###')


# Function to send environment data to the server
def send_environment(environment_data, box_id):
    r = requests.post(serverUrl + "environment/" + box_id, json=environment_data)
    print("Environment Data send with the corresponding environment_id: ")
    print(r.content)
    logger.info('Environment Data send to Server')
    logger.debug('Environment Post Request Data: URL: %s ; status_code: %s; Text: %s ;json: %s' %
                 (r.url, r.status_code, r.text, environment_data))


# Function to send a movement to the server
def send_movement(files, box_id):
    r = requests.post(serverUrl + "movement/" + box_id, files=files)
    print("Movement Data send with the corresponding movement_id: ")
    print(r.content)
    logger.info('Movement Data send with to Server')
    logger.debug('Movement Post Request Data: URL: %s ; status_code: %s; Text: %s ;Content: %s' %
                 (r.url, r.status_code, r.text, files))


# Function to track a environment
def track_environment():
    try:
        print("Collect Environment Data")
        logger.info('Collect Environment Data')
        environment = {}
        environment["date"] = str(datetime.now())
        environment["temperature"] = dht22.temperature
        environment["humidity"] = dht22.humidity

        print("Environment Data: ")
        print(environment)
        logger.info('Environment Data: %s' % environment)
        send_environment(environment, boxId)

        global environmentData
        environmentData = environment
    except Exception as e:
        print(e)
        logger.exception(e, exc_info=True)


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

            if (weight < weightThreshold and len(values) == 0):
                print("Waiting for movement! (currently measured weight: " + str(weight) + ")")
                # noinspection SyntaxError
                logger.debug('Waiting for movement! (currently measured weight: ' + str(weight) + ')')

            # start movement if weight higher than threshold is recognized
            if (weight > weightThreshold and len(values) == 0):
                print("Movement recognized!")
                logger.info('Movement recognized!')
                recorder = Process(target=record)
                recorder.start()

                movementStartDate = datetime.now()

                camera.wait_recording(1)  # continue camera recording

                values.append(weight)  # add current weight to weight list


            else:
                # continue movement if currently recognized weight is above threshold
                if (weight > weightThreshold):
                    values.append(weight)
                    camera.wait_recording(1)

                    print("Currently measured weight: " + str(weight))
                    logger.info("Currently measured weight: " + str(weight))

            hx.power_down()
            hx.power_up()

            # stop movement if weight is below threshold
            if (weight < weightThreshold):
                if (len(values) >= 1):
                    print("Movement ending!")
                    logger.info("Movement ending!")
                    movementEndDate = datetime.now()

                    duration = (movementEndDate - movementStartDate).total_seconds()
                    stream.copy_to('/home/pi/station/files/' + str(movementStartDate) + '.h264', seconds=duration + 5)
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
                            recorder.terminate()
                            print("terminated recorder")
                            logger.info("terminated recorder")
                    except:
                        print("no alive recorder")
                        logger.warning('no alive recorder')
                    files['audioKey'] = (os.path.basename("/home/pi/station/files/sound.wav"),
                                         open("/home/pi/station/files/sound.wav", 'rb'))
                    files['videoKey'] = (os.path.basename('/home/pi/station/files/' + str(movementStartDate) + '.h264'),
                                         open('/home/pi/station/files/' + str(movementStartDate) + '.h264', 'rb'))

                    if (environmentData != None):
                        movementData["environment"] = environmentData

                    else:
                        movementData["environment"] = {}

                    print("Movement Data: ")
                    print(movementData)
                    logger.info("Movement Data: %s" % movementData)
                    files["json"] = (None, json.dumps(movementData), 'application/json')

                    send_movement(files, boxId)

                    values = []
                    os.remove('/home/pi/station/files/sound.wav')
                    os.remove('/home/pi/station/files/' + str(movementStartDate) + '.h264')
        except (KeyboardInterrupt, SystemExit):
            #    cleanAndExit()
            logger.exception('program terminated', exc_info=True)


print("Start Birdiary!")
logger.info("##### Start Birdiary! #####")
track_movement()
sys.stderr.close()
