#!/usr/bin/env python3

import subprocess
# import sys
# import time
import paho.mqtt.client as mqtt
# import os
import json

from config import (
    mqtt_user, mqtt_pass, mqtt_host,
    mqtt_port, mqtt_topic, mqtt_qos, freq
)

rtl_433_cmd = "/usr/local/bin/rtl_433 -f {0} -G -F json".format(freq)  # linux


# Define MQTT event callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


def on_message(client, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_publish(client, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(client, obj, level, string):
    print(string)


# Setup MQTT connection
mqttc = mqtt.Client()
# Assign event callbacks
# mqttc.on_message = on_message
mqttc.on_connect = on_connect
# mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_disconnect = on_disconnect

# Uncomment to enable debug messages
# mqttc.on_log = on_log

# Uncomment the next line if your MQTT server requires authentication
mqttc.username_pw_set(mqtt_user, password=mqtt_pass)
mqttc.connect(mqtt_host, mqtt_port, 60)

mqttc.loop_start()

# Start RTL433 listener
rtl433_proc = subprocess.Popen(
    rtl_433_cmd.split(),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True)


while True:
    for line in iter(rtl433_proc.stdout.readline, '\n'):
        if "time" in line:
            if 'id' in line:
                json_dict = json.loads(line)
                device_id = str(json_dict.pop('id'))
                mqttc.publish(
                    mqtt_topic+"/"+device_id,
                    payload=json.dumps(json_dict),
                    qos=mqtt_qos,
                    retain=True
                )
            else:

                mqttc.publish(
                    mqtt_topic, payload=line, qos=mqtt_qos)
