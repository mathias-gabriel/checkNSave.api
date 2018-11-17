import paho.mqtt.client as mqtt
import time
import datetime

import ConfigParser
from pymongo import MongoClient


def buildMessage(value):

    dt = datetime.datetime.now()
    date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    date_unix = time.mktime(dt.timetuple())
    print(date_str)
    print(date_unix)
    message = {
        "date": int(date_unix) ,
        "date_str": date_str ,
        "value": value
    }
    return message


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("home/mathias")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print( msg.topic+" "+str(msg.payload))

    message = buildMessage( str(msg.payload) )
    print(message)
    try:
        iot_messages = db.iot_messages
        print( iot_messages.insert_one(message).inserted_id )
    except :
        print "duplicate:"




if __name__ == "__main__":


    print "chargement de la configuration:"
    config = ConfigParser.RawConfigParser()
    config.read('conf/app.conf')

    mongoHost           = config.get('mongo', 'host')
    mongoDB             = config.get('mongo', 'db')


    client = MongoClient(mongoHost)
    db = client[mongoDB]

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("mosquitto", 1883, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()





