import os
import json
import logging
from flask import Flask, request, jsonify, Response
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
from datetime import datetime
from pathlib import Path
import arrow
from recordgen import *
import paramiko
import shutil
import subprocess

ORG_NAME = os.environ.get('ORG_NAME')
sip_server = os.environ.get('SIP_SERVER')
sip_server_username = os.environ.get('SIP_SERVER_USERNAME')
sip_server_sshkey = os.environ.get('SIP_SERVER_SSHKEY')
sip_trunk = os.environ.get('SIP_TRUNK')
sip_destination_number = os.environ.get('DESTINATION_NUMBER','').split(',')
sip_recording = os.environ.get('SIP_CALLERID')
sip_callfile_path = os.environ.get('SIP_CALLFILE_PATH')
sip_callerid = os.environ.get('SIP_CALLERID')

app = Flask(__name__)

@app.route('/callalert', methods=['POST'])
def callalert():
    if request.method == 'POST':
        if request.content_type != 'application/json':
            return Response('Invalid content-type. Must be application/json.', status=415)

        timestamp = workdir_init()[0]
        work_dir_parent = workdir_init()[1]
        data = request.json

        trigger_name = data["trigger_name"]
        trigger_severity = data["trigger_severity"]

        #print(f"{ORG_NAME} System Alert, Attention Required, {trigger_name} alert triggered, {trigger_severity} Severity")
        alert_text = f"{ORG_NAME} System Alert, Attention Required, {trigger_name} alert triggered, {trigger_severity} Severity"
        print(alert_text)
        f = open(f"{work_dir_parent}/soundtext/alert-{timestamp}.txt", "w")
        f.write(alert_text)
        f.close()

        gen_recording(timestamp, trigger_name, trigger_severity)

        upload_recording(work_dir_parent, timestamp)

        for n in sip_destination_number:
            callfile(work_dir_parent, timestamp, n)
            upload_callfile(work_dir_parent, timestamp, n)

        return jsonify(
            status = True,
            message = f"Call Alert Successfull - Call Message: {alert_text}"
        )

@app.route('/callalert/prometheus', methods=['POST'])
def prometheus():
    if request.method == 'POST':
        if request.content_type != 'application/json':
            return Response('Invalid content-type. Must be application/json.', status=415)
    
        timestamp = workdir_init()[0]
        work_dir_parent = workdir_init()[1]
        print(timestamp)
        print(work_dir_parent)
        data = request.json

        item_dict = data
        trigger_len = len(item_dict['alerts'])
        trigger_job = ""
        for n in range(trigger_len):
            trigger_name = item_dict["alerts"][n]["labels"]["alertname"]
            trigger_severity = item_dict["alerts"][n]["labels"]["severity"]
            trigger_job_item = item_dict["alerts"][n]["labels"]["job"]
            #trigger_name = data["alerts"][0]["labels"]["alertname"]
            #trigger_severity = data["alerts"][0]["labels"]["severity"]
            trigger_job = f'{trigger_job} and {trigger_job_item}' if trigger_job else trigger_job_item

        alert_text = f"{ORG_NAME} System Alert, Attention Required, {trigger_name} alert triggered in {trigger_job}, {trigger_severity} Severity"
        print(alert_text)
        f = open(f"{work_dir_parent}/soundtext/alert-{timestamp}.txt", "w")
        f.write(alert_text)
        f.close()

        gen_recording(timestamp, trigger_name, trigger_severity)
        upload_recording(work_dir_parent, timestamp)

        for n in sip_destination_number:
            callfile(work_dir_parent, timestamp, n)
            upload_callfile(work_dir_parent, timestamp, n)

        return jsonify(
            status = True,
            message = f"Call Alert Successfull - Call Message: {alert_text}"
        )

def workdir_init():
    dt = datetime.now()
    ts = datetime.timestamp(dt)
    date_time = datetime.fromtimestamp(ts)
    timestamp = date_time.strftime("%Y_%m_%d-%H_%M_%S")
    work_dir_parent = "/tmp/callalert/"
    work_dirs = ["/tmp/callalert/sounds", "/tmp/callalert/soundtext", "/tmp/callalert/callfile" ]
    for wd in work_dirs:
        Path(wd).mkdir(parents=True, exist_ok=True)
    deltime = arrow.now().shift(minutes=-5) #.shift(days=-1)
    for files in Path(work_dir_parent).rglob('*'):
        if files.is_file():
            itemTime = arrow.get(files.stat().st_mtime)
            if itemTime < deltime:
                os.remove(files)
    return(timestamp,work_dir_parent)

def upload_recording(work_dir_parent, timestamp):
    src_path = work_dir_parent + "/sounds/alert-" + timestamp + ".wav"
    dest_path = "/var/lib/asterisk/sounds/alert-" + timestamp + ".wav"
    shutil.copy(src_path, dest_path)
    subprocess.run(['chown', 'asterisk:asterisk', dest_path])
    subprocess.run(['chmod', '0664', dest_path])

def upload_callfile(work_dir_parent, timestamp, destination_number):
    src_path = work_dir_parent + "/callfile/alert-" + timestamp + "-" + destination_number + ".call"
    dest_path = sip_callfile_path + "/alert-" + timestamp + "-" + destination_number + ".call"
    shutil.copy(src_path, dest_path)
    
def callfile(work_dir_parent, timestamp, destination_number):
    content = f"""Channel: SIP/{sip_trunk}/{destination_number}
CallerID: {sip_callerid}
Application: Playback
Data: alert-{timestamp}"""
    f = open(f"{work_dir_parent}/callfile/alert-{timestamp}-{destination_number}.call", "w")
    f.write(content)
    f.close()




