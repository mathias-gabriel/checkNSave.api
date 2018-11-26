#! /usr/bin/env python
#-*-coding:utf-8-*-

from flask import Flask, request, jsonify
from flask_restful import Resource, Api

from gevent import pywsgi

from flasgger import Swagger
import configparser
import psycopg2
from pymongo import MongoClient, ASCENDING, DESCENDING

from google.cloud import vision
from google.cloud.vision import types
import io
import os

import numpy as np
import cv2 as cv

import uuid

from keras.preprocessing.image import img_to_array
import imutils
import cv2
from keras.models import load_model
import numpy as np

from geopy.geocoders import Nominatim

app                         = Flask(__name__)
app.config['SECRET_KEY']    = 'secret!'
api         = Api(app)
UPLOAD_FOLDER = os.path.basename('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/upload', methods=['POST'])
def upload_file():

    """Example endpoint returning a list of colors by palette
     This is using docstrings for specifications.
     ---
     parameters:
        - name: image
          required: false
          in: formData
          type: file

     responses:
       200:
         description: A list of colors (may be filtered by palette)
    """

    file = request.files['image']
    f = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) )
    
    # add your custom code to check that the uploaded file is a valid image and not a malicious file (out-of-scope for this post)
    file.save(f)


    # on analyse l'image pour detecter si il y a un visage
    img = cv.imread(f)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    emotion_classifier = load_model(emotion_model_path, compile=False)
    EMOTIONS = ["angry" ,"disgust","scared", "happy", "sad", "surprised",
     "neutral"]

    face_detected = False
    face_label = ""
    if len( faces ) > 0:
        face_detected = True

        faces = sorted(faces, reverse=True, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
        (fX, fY, fW, fH) = faces
        # Extract the ROI of the face from the grayscale image, resize it to a fixed 28x28 pixels, and then prepare
        # the ROI for classification via the CNN
        roi = gray[fY:fY + fH, fX:fX + fW]
        roi = cv2.resize(roi, (64, 64))
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)

        preds = emotion_classifier.predict(roi)[0]
        emotion_probability = np.max(preds)
        face_label = EMOTIONS[preds.argmax()]

    



    # on enrichie avec google vision
    labelGoogleVision = getLabelGoogleVision(f)

    response = {
        "face_detected":face_detected,
        "face_description":face_label,
        "google_vision_labels":labelGoogleVision
    }
    return jsonify( response )

@app.route('/defibrilatteurs/<lat>/<lng>/<position>/<limit>', methods=['GET'])
def getDefibrillatteurs(lat, lng, position, limit):

    """Example endpoint returning a list of colors by palette
     This is using docstrings for specifications.
     ---
     parameters:
       - name: lat
         in: path
         type: double

       - name: lng
         in: path
         type: double

       - name: position
         in: path
         type: integer

       - name: limit
         in: path
         type: integer

     responses:
       200:
         description: A list of colors (may be filtered by palette)
     """

    cur = conn.cursor()
    try:
        query = "SELECT nom, adress, ville, st_Distance( st_Transform(geom, 2154), st_Transform( st_GeomFromText( 'POINT("+str(float(lat))+" "+str(float(lng))+")', 4326) , 2154) ) as distance FROM defibrillateurs ORDER BY distance OFFSET "+str(int(position))+" LIMIT "+str(int(limit))+";"
        #cur.execute("select titre, localisatio, ville, telephone, st_Distance( st_Transform(geom, 2154), st_Transform( st_GeomFromText( 'POINT( "+str(float(lat))+" "+str(float(lng))+")', 4326) , 2154) ) as distance from \"france_issy-les-moulineaux_defibrillateurs\" OFFSET "+str(int(position))+" LIMIT "+str(int(limit))+";" )
        cur.execute(query)
    except:
        print("I can't SELECT from bar")


    rows = cur.fetchall()
    print("\nRows: \n")
    defibrilatteurs = []

    for row in rows:
        defibrilatteurs.append( {"name": row[0], "localisatio": row[1],  "ville": row[2] ,"distance": row[3] } )
        print("   ", row[0], "   ", row[1])

    return jsonify( defibrilatteurs )

@app.route('/address/<lat>/<lng>', methods=['GET'])
def getAddress(lat, lng):

    """Example endpoint returning a list of colors by palette
     This is using docstrings for specifications.
     ---
     parameters:
       - name: lat
         in: path
         type: double

       - name: lng
         in: path
         type: double

     responses:
       200:
         description: A list of colors (may be filtered by palette)
     """

    latlng = str(lat)+" "+str(lng)
    geolocator = Nominatim(user_agent="checknsave")
    location = geolocator.reverse(latlng)

    response = {
        "address":location.address
    }

    return jsonify( response )


@app.route('/messages', methods=['GET'])
def getGeonameInText():

    """
    This examples uses FlaskRESTful Resource
    It works also with swag_from, schemas and spec_dict
       ---
       responses:
         200:
           description: A single user item
           schema:
             message: string
    """

    iot_messages = []
    for message in db.iot_messages.find({}).sort([("date", DESCENDING) ]) :
        iot_messages.append( {"date": message["date_str"] ,"message": message["value"] } )

    return jsonify( iot_messages )


def getLabelGoogleVision(path):

    client = vision.ImageAnnotatorClient()

    image_file = io.open(path, 'rb') # Open image 
    content = image_file.read() # Read image into memory
    image = types.Image(content=content) # Takes image and turns it into something that Google's API will understand 
    response = client.label_detection(image=image) # Gets response from API for image 
    labels = response.label_annotations
    print("getLabelGoogleVision")

    results = []
    for label in labels:

        l= {
            "description":label.description,
            "score":label.score
        }
        print(l)
        results.append(l)

    print(results)
    return results


if __name__ == '__main__':

    print("chargement de la configuration:")

    config = configparser.RawConfigParser()
    config.read('/root/conf/app.conf')

    postgisDbname       = config.get('postgresql', 'dbname')
    postgisUser         = config.get('postgresql', 'user')
    postgisHost         = config.get('postgresql', 'host')
    postgisPassword     = config.get('postgresql', 'password')

    conn = psycopg2.connect("dbname='"+postgisDbname+"' user='"+postgisUser+"' host='"+postgisHost+"' password='"+postgisPassword+"'")

    mongoHost           = config.get('mongo', 'host')
    mongoDB             = config.get('mongo', 'db')

    client = MongoClient(mongoHost)
    db = client[mongoDB]

    detection_face_path = 'haarcascade_files/haarcascade_frontalface_default.xml'
    detection_eye_path = 'haarcascade_files/haarcascade_eye.xml'
    emotion_model_path = 'models/_mini_XCEPTION.102-0.66.hdf5'

    face_cascade = cv.CascadeClassifier(detection_face_path)
    eye_cascade = cv.CascadeClassifier(detection_eye_path)

    Swagger(app)
    app.run(host='0.0.0.0', port='5003')
    #server = pywsgi.WSGIServer(('', 5002), app, handler_class=WebSocketHandler)
    #server.serve_forever()