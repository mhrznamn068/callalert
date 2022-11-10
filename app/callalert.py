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

        data = request.json

        trigger_name = data["trigger_name"]
        trigger_severity = data["trigger_severity"]

        #print(f"{ORG_NAME} System Alert, Attention Required, {trigger_name} alert triggered, {trigger_severity} Severity")
        alert_text = f"{ORG_NAME} System Alert, Attention Required, {trigger_name} alert triggered, {trigger_severity} Severity"
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
            message = "Call Alert Successfull"
        )

def upload_recording(work_dir_parent, timestamp):
    try:
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(sip_server, username=sip_server_username, key_filename=sip_server_sshkey)
    except paramiko.ssh_exception.AuthenticationException:
        print('SIP server Authentication Error')
        sys.exit()
    sftp = ssh.open_sftp()
    sftp.put(f"{work_dir_parent}/sounds/alert-{timestamp}.wav", f'/var/lib/asterisk/sounds/alert-{timestamp}.wav')
    sftp.close()
    command = f'chown -R asterisk:asterisk /var/lib/asterisk/sounds/alert-{timestamp}.wav && chmod 664 /var/lib/asterisk/sounds/alert-{timestamp}.wav && find /var/lib/asterisk/sounds -name "alert-*" -amin +5 -delete -print'
    (stdin, stdout, stderr) = ssh.exec_command(command)
    for line in stdout.readlines():
        print(line)
    ssh.close()

def upload_callfile(work_dir_parent, timestamp, destination_number):
    try:
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(sip_server, username=sip_server_username, key_filename=sip_server_sshkey)
    except paramiko.ssh_exception.AuthenticationException:
        print('SIP server Authentication Error')
        sys.exit()
    sftp = ssh.open_sftp()
    sftp.put(f"{work_dir_parent}/callfile/alert-{timestamp}-{destination_number}.call", f'{sip_callfile_path}/alert-{timestamp}-{destination_number}.call')
    sftp.close()
    
def callfile(work_dir_parent, timestamp, destination_number):
    content = f"""Channel: SIP/{sip_trunk}/{destination_number}
CallerID: {sip_callerid}
Application: Playback
Data: alert-{timestamp}"""
    f = open(f"{work_dir_parent}/callfile/alert-{timestamp}-{destination_number}.call", "w")
    f.write(content)
    f.close()




