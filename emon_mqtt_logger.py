#!/usr/bin/env python

import sys
import os
import re
import json
import argparse
import ConfigParser
import paho.mqtt.client as mqtt
import requests
from datetime import datetime

CONFIG_PATH = '/etc/sensors/config'

def load_config(path):
    cfg = ConfigParser.RawConfigParser()
    with open(path, 'r') as f:
        cfg.readfp(f)

    return {
        'mqtt_user': cfg.get('mqtt', 'user'),
        'mqtt_password': cfg.get('mqtt', 'password'),
        'emoncms_apikey': cfg.get('emoncms', 'apikey'),
        'emoncms_url': cfg.get('emoncms', 'url'),
        'emonhub_bastopic': cfg.get('emonhub', 'basetopic'),
        }

def mqtt_logger(emoncms, apikey, basetopic, mqtt_user, mqtt_password):
    emoncms_post_url = "%s/input/post.json" % emoncms
    def on_connect(client, userdata, flags, rc):
        if rc:
            print "Error connecting, rc %d" % rc
            return
        subscription = "%s/#" % basetopic
        print "Subscribing to %s" % subscription
        client.subscribe(subscription)

    def on_message(client, userdata, msg):
        subtopic = msg.topic[len(basetopic) + 1:]

        m = re.match(r'^([^/]*)/([^/]*)$', subtopic)
        if not m or len(m.groups()) != 2:
            print "Couldn't extract node/input - ignoring."
            return

        node = m.groups()[0]
        inp = m.groups()[1]
        try:
            value = float(msg.payload)
        except:
            print "Error parsing value %s" % msg.payload
            return

        # Post to emoncms:
        # input/post.json?node=10&json={power1:100}
        json_string = json.dumps({inp: value})
        params = {'node': node, 'json': json_string, 'apikey': apikey}
        resp = requests.post(emoncms_post_url, params=params)
        if resp.status_code != 200:
            print 'Error posting to emoncms: status %d:' % resp.status_code
            print resp.content

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(mqtt_user, mqtt_password)

    client.connect("localhost", 1883, 60)
    client.loop_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Archive emonhub data from an mqtt topic to emoncms")
    parser.add_argument("-c", default=CONFIG_PATH, dest='config_path',
        help='Path to config file')
    args = parser.parse_args()

    config = load_config(args.config_path)

    mqtt_logger(config['emoncms_url'], config['emoncms_apikey'],
                config['emonhub_bastopic'], config['mqtt_user'],
                config['mqtt_password'])
