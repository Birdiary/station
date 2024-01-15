import time
from paho.mqtt import client as mqtt_client
import threading
import json
import os
import logging


class SendMQTT(threading.Thread):
    def __init__(self, brokerIP: str, username: str, password: str, brokerPort: int = 1883):
        super().__init__()
        self.BrokerIP = brokerIP
        self.BrokerPort = brokerPort
        self.Username = username
        self.Password = password
        self.MyClient = mqtt_client.Client()
        self.connection_alive = False
        self.Serial = None
        self.Cmnd = None
        self.CmndValue = None
        self.logger = logging.getLogger('main.mqtt')

    def __on_message(self, client, userdata, message):
        print(f"Message: {message.topic} {message.payload.decode('utf-8')}")
        myStringArray = message.topic.split('/')
        self.Serial, self.Cmnd, self.CmndValue = myStringArray[1], myStringArray[3], message.payload.decode('utf-8')
        self.receivedCmnd()

    def __on_connect(self, client='', userdata='', flags='', rc=''):
        if rc == 0:
            print(client, userdata)
            print("connected OK")
            self.logger.info("MQTT connected OK")
            self.connection_alive = True
        else:
            print("Bad connection Return code=", rc, client, userdata, flags)
            self.logger.info(f"Bad connection Return code={rc}")
            self.connection_alive = False

    def __on_disconnect(self, client='', userdata='', rc=''):
        print("Client disconnected")
        self.logger.info("Connection to Broker disconnected")
        self.connection_alive = False

    def __on_subscribe(self, client, userdata, mid, granted_qos):
        print("Mid", client, userdata, mid, granted_qos)
        return rc

    def run(self):
        self.MyClient.on_connect = self.__on_connect
        self.MyClient.on_disconnect = self.__on_disconnect
        self.MyClient.on_subscribe = self.__on_subscribe
        self.MyClient.on_message = self.__on_message
        self.MyClient.loop_start()
        self.MyClient.username_pw_set(username=self.Username, password=self.Password)
        rc = self.MyClient.connect(self.BrokerIP, self.BrokerPort, 30)
        self.logger.debug(f"Broker connect() Return code={rc}")

    def closeConnection(self):
        rc = self.MyClient.disconnect()
        self.logger.info("Connection to broker disconnected")

    def sendData(self, topic: str, jdata):
        MyTopic = topic
        self.MyClient.publish(MyTopic, str(jdata))

    def discover_HASS(self, station_id: str):
        print("Home Assistant discover")
        self.logger.info("Home Assistant discover")
        # sensor_types: sensor_type, unit_of_measurement, name, device_class,topic,icon
        sensor_types = [
            ("temperature", "°C", "temperature", "temperature", "environment", "mdi:temperature-celsius"),
            ("humidity", "%", "humidity", "humidity", "environment", "mdi:water-percent"),
            ("movement_duration", None, "duration", None, "movement", "mdi:timer-marker-outline"),
            ("movement_id", None, "id", None, "movement", "mdi:identifier"),
            ("station_id", None, "station_id", None, "movement", "mdi:id-card"),
            ("weight", "g", "weight", "weight", "movement", "mdi:weight-gram"),
            # ("foodlevel", "%", "foodlevel", "mdi:gauge"),
            # ("pressure", "hPa", "pressure", "pressure"),
            # ("illuminance", "lx", "illuminance", "illuminance"),
        ]

        for sensor_type, unit, name, device_class, topic, icon in sensor_types:
            mytopic = os.path.join("homeassistant", "sensor", f"birdiary_{station_id}_{sensor_type}", "config")
            mpayload = {
                "state_topic": os.path.join("birdiary", station_id, topic),
                "unit_of_measurement": unit,
                "value_template": f"{{{{value_json.{name}}}}}",
                "icon": icon,
                "name": f"birdiary_{sensor_type}",
                "unique_id": f"birdiary_{station_id}_{sensor_type}",
                "device_class": device_class,
                "device": {
                    "name": f"birdiary_station_{station_id[:8]}",
                    "manufacturer": "wiediversistmeingarten.org",
                    "identifiers": f"{station_id}",
                    "model": "birdiary_station"
                }
            }
            self.MyClient.publish(mytopic, json.dumps(mpayload))
            time.sleep(0.5)
        sensor_types = [
            ("movement", "start_date", "timestamp", "movement"),
        ]
        for sensor_type, name, device_class, topic in sensor_types:
            mytopic = os.path.join("homeassistant", "sensor", f"birdiary_{station_id}_{sensor_type}", "config")
            mpayload = {
                "state_topic": os.path.join("birdiary", station_id, topic),
                "value_template": f"{{{{value_json.{name}}}}}",
                "name": f"birdiary_{sensor_type}",
                "icon": "mdi:bird",
                "unique_id": f"birdiary_{station_id}_{sensor_type}",
                "device_class": device_class,
                "device": {
                    "name": f"birdiary_station_{station_id[:8]}",
                    "manufacturer": "https://wiediversistmeingarten.org",
                    "identifiers": f"{station_id}",
                    "model": "birdiary_station"
                }
            }
            self.MyClient.publish(mytopic, json.dumps(mpayload))
            time.sleep(0.5)
