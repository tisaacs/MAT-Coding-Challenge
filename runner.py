import datetime
import glob
import json
import logging
import os
import sys

import paho.mqtt.client as mqtt
from telemetry.car_manager import CarManager
from telemetry.track_lookup import TrackLookup

car_manager = None
logger = None
env = None
client = None


def main():
    read_envs()
    setup_logging(log_to_file=True)

    logger.debug('Config is:\n\n' + str(env))

    initialise()

    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    car_manager.subscribe_to_car_status_events(new_car_status_event)

    mqtt_address = env['MQTT_ADDRESS']
    mqtt_keepalive = int(env['MQTT_KEEPALIVE'])

    logger.info(f'Connecting to MQTT address {mqtt_address} and keepalive {mqtt_keepalive}')

    client.connect(mqtt_address, keepalive=mqtt_keepalive)

    client.loop_forever()


def initialise():
    global car_manager

    track_coordinates_path = env['TRACK_COORDINATES_PATH']
    logger.debug(f'Creating track_lookup using file {track_coordinates_path}')
    track_lookup = TrackLookup(track_coordinates_path)
    logger.debug('Done')

    car_count = int(env['CAR_COUNT'])
    logger.debug(f'Creating car_manager with {car_count} cars')
    car_manager = CarManager(car_count, track_lookup)
    logger.debug('Done')


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logger.info(f'Connected with code {rc}')

    mqtt_topic = env['MQTT_TOPIC']
    logger.info(f'Subscribing to topic {mqtt_topic}')
    client.subscribe(mqtt_topic)
    logger.debug('Subscribed to topic')


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    car_manager.new_car_data(data)


def new_car_status_event(event):
    topic = env['CAR_STATUS_TOPIC']
    data = json.dumps(event)
    client.publish(topic, data)


def setup_logging(log_to_file):
    global logger
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    controller = None

    nowstring = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_name = 'telemetry_{0}.log'.format(nowstring)

    logger = logging.getLogger('telemetry')
    log_level = env['LOG_LEVEL']
    logger.setLevel(log_level)
    fileHandler = logging.FileHandler('./logs/{0}'.format(log_file_name))
    stdoutHandler = logging.StreamHandler(sys.stdout)
    fileHandler.setFormatter(logging.Formatter(log_format))
    stdoutHandler.setFormatter(logging.Formatter(log_format))

    logger.addHandler(stdoutHandler)

    if log_to_file:
        logger.info('Logging to ./logs/{0}'.format(log_file_name))
        logger.addHandler(fileHandler)


def read_envs():
    global env
    env = {}
    for file_path in glob.glob('*.env'):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#') == False:
                split = stripped.split('=')
                key = split[0]
                value = split[1]

                env[key] = value


if __name__ == '__main__':
    main()
