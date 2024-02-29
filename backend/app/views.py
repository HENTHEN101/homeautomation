"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

# from crypt import methods

from app import app, Config,  mongo, Mqtt
from flask import escape, render_template, request, jsonify, send_file, redirect, make_response, send_from_directory 
from json import dumps, loads 
from werkzeug.utils import secure_filename
from datetime import datetime,timedelta, timezone
from os import getcwd
from os.path import join, exists
from time import time, ctime
from math import floor
 



#####################################
#   Routing for your application    #
#####################################


# 1. CREATE ROUTE FOR '/api/set/combination'

@app.route('/api/set/combination', methods=['POST'])
def update_passcode():
# Retrieve the passcode from the 'code' collection in the databas
    passcode = request.json.get('code')

    print(f"passcode: {passcode}")

    if request.method == "POST" :
        try:
                # Update the document in the 'code' collection with the new passcode
                item= mongo.setPass(passcode)
                if item:
                    return jsonify({"status":"complete","data":"complete"})
        except Exception as e:
            msg=str(e)  
            print(f"update_pwd Error: f{msg}")
        return jsonify({"status":"failed","data":"failed"})

    
# 2. CREATE ROUTE FOR '/api/check/combination'
@app.route('/api/check/combination', methods=['POST'])
def check_passcode():
    '''Checks if the passcode is correct'''
    if request.method == "POST":
        try:
            form = request.form
            passcode = form.get('passcode')
            if passcode:
                # CHECK IF PASSCODE EXISTS IN THE 'code' COLLECTION
                result = mongo.count_passcodes(passcode)
                if result != 0:
                    return jsonify({"status":"success","data":"complete"})
        except Exception as e:
            print(f"check_passcode() error: {e}")
        
        return jsonify({"status":"failed","data":"failed"})
    


# 3. CREATE ROUTE FOR '/api/update'
@app.route('/api/update', methods=['POST'])
def update_radar():
    '''Updates the 'radar' collection'''
    if request.method == "POST":
        try:
            jsonDoc= request.get_json()
            # Update the document in the 'code' collection with the new passcode

            timestamp = datetime.now().timestamp()
            timestamp = floor(timestamp)
            jsonDoc['timestamp'] = timestamp

            Mqtt.publish("620152511",mongo.dumps(jsonDoc))
            # Mqtt.publish("620156144_pub",mongo.dumps(jsonDoc))
            Mqtt.publish("620152511_sub",mongo.dumps(jsonDoc))

            print(f"MQTT: {jsonDoc}")

            item = mongo.insertData(jsonDoc)
            if item:
                return jsonify({"status": "complete", "data": "complete"})
        except Exception as e:
            msg = str(e)
            print(f"update Error: {msg}")
        return jsonify({"status": "failed", "data": "failed"})
   
# 4. CREATE ROUTE FOR '/api/reserve/<start>/<end>'
@app.route('/api/reserve/<start>/<end>', methods=['GET'])
def get_reserve_radar(start, end):
    '''Returns the 'reserve' field/variable, using all documents found between specified start and end timestamps'''
    if request.method == "GET":
        try:
            start = int(start)
            end = int(end)

            result = list(mongo.retrieve_radar(start,end))
            if result:
                return jsonify({"status":"success","data":result})
        except Exception as e:
            print(f"get_reserve_radar() error: {e}")
    
        return jsonify({"status":"failed","data":"failed"})

# 5. CREATE ROUTE FOR '/api/avg/<start>/<end>'
@app.route('/api/avg/<start>/<end>', methods=['GET'])
def get_average_radar(start, end):
    '''Returns the average of the 'reserve' field/variable, using all documents found between specified start and end timestamps'''
    
    try:
        start = int(start)
        end = int(end)

        result = list(mongo.average_radar(start, end))
        if result:
            return jsonify({"status":"success","data":result})
    except Exception as e:
        print(f"get_average_radar() error: {e}")
    
    return jsonify({"status":"failed","data":"failed"})


@app.route('/api/file/get/<filename>', methods=['GET']) 
def get_images(filename):   
    '''Returns requested file from uploads folder'''
   
    if request.method == "GET":
        directory   = join( getcwd(), Config.UPLOADS_FOLDER) 
        filePath    = join( getcwd(), Config.UPLOADS_FOLDER, filename) 

        # RETURN FILE IF IT EXISTS IN FOLDER
        if exists(filePath):        
            return send_from_directory(directory, filename)
        
        # FILE DOES NOT EXIST
        return jsonify({"status":"file not found"}), 404


@app.route('/api/file/upload',methods=["POST"])  
def upload():
    '''Saves a file to the uploads folder'''
    
    if request.method == "POST": 
        file     = request.files['file']
        filename = secure_filename(file.filename)
        file.save(join(getcwd(),Config.UPLOADS_FOLDER , filename))
        return jsonify({"status":"File upload successful", "filename":f"{filename}" })

 


###############################################################
# The functions below should be applicable to all Flask apps. #
###############################################################


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(405)
def page_not_found(error):
    """Custom 404 page."""    
    return jsonify({"status": 404}), 404