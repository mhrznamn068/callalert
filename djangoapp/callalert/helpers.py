import os
import json
import logging
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
from datetime import datetime
from pathlib import Path
import arrow
import paramiko
from django.conf import settings

SIP_SERVER = settings.SIP_SERVER
SIP_SERVER_USERNAME = settings.SIP_SERVER_USERNAME
SIP_SERVER_SSHKEY = settings.SIP_SERVER_SSHKEY
SIP_TRUNK = settings.SIP_TRUNK
SIP_DESTINATION_NUMBER = settings.SIP_DESTINATION_NUMBER
SIP_RECORDING = settings.SIP_RECORDING
SIP_CALLFILE_PATH = settings.SIP_CALLFILE_PATH
SIP_CALLERID = settings.SIP_CALLERID

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
    try:
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(SIP_SERVER, username=SIP_SERVER_USERNAME, key_filename=SIP_SERVER_SSHKEY)
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
      ssh.connect(SIP_SERVER, username=SIP_SERVER_USERNAME, key_filename=SIP_SERVER_SSHKEY)
    except paramiko.ssh_exception.AuthenticationException:
        print('SIP server Authentication Error')
        sys.exit()
    sftp = ssh.open_sftp()
    callfile = f"{work_dir_parent}callfile/alert-{timestamp}-{destination_number}.call"
    print(callfile)
    callfile_dst_path = f'{SIP_CALLFILE_PATH}alert-{timestamp}-{destination_number}.call'
    print(callfile_dst_path)
    sftp.put(f"{work_dir_parent}callfile/alert-{timestamp}-{destination_number}.call", f'/var/spool/asterisk/tmp/alert-{timestamp}-{destination_number}.call')
    ssh.exec_command(f'mv /var/spool/asterisk/tmp/alert-{timestamp}-{destination_number}.call /var/spool/asterisk/outgoing/alert-{timestamp}-{destination_number}.call')
    sftp.close()
    
def callfile(work_dir_parent, timestamp, destination_number):
    content = f"""Channel: SIP/{SIP_TRUNK}/{destination_number}
CallerID: {SIP_CALLERID}
Application: Playback
Data: alert-{timestamp}"""
    f = open(f"{work_dir_parent}callfile/alert-{timestamp}-{destination_number}.call", "w")
    f.write(content)
    f.close()