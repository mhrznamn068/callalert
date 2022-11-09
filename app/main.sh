#!/bin/bash

TIMESTAMP=$(date +%Y_%m_%d-%H_%M_%S)

# Create call file directory
[ -d "/tmp/callalert/sounds" ] && echo "Directory /tmp/callalert/sounds exists." || mkdir -p /tmp/callalert/sounds
[ -d "/tmp/callalert/soundtext" ] && echo "Directory /tmp/callalert/soundtext exists." || mkdir -p /tmp/callalert/soundtext
[ -d "/tmp/callalert/callfile" ] && echo "Directory /tmp/callalert/callfile exists." || mkdir -p /tmp/callalert/callfile
find /tmp/callalert -mtime +1 -delete -print

TRIGGER_NAME=$(head -n 1 /tmp/callalert/soundtext/alert.txt)
TRIGGER_SEVERITY=$(head -n 2 /tmp/callalert/soundtext/alert.txt)

echo "${ORG_NAME} System Alert, Attention Required, ${TRIGGER_NAME} alert triggered, ${TRIGGER_SEVERITY} Severity" > /tmp/callalert/soundtext/alert-${TIMESTAMP}.txt
python3 ./recordgen.py ${TIMESTAMP} ${TRIGGER_SEVERITY} >> /var/log/callalert/callalert-${TIMESTAMP}.log
scp -i ${SIP_SERVER_SSHKEY} /tmp/callalert/sounds/alert-${TIMESTAMP}.wav root@${SIP_SERVER}:/var/lib/asterisk/sounds/
ssh -i ${SIP_SERVER_SSHKEY} root@${SIP_SERVER} "chown -R asterisk:asterisk /var/lib/asterisk/sounds/alert-${TIMESTAMP}.wav && find /var/lib/asterisk/sounds -name "alert-*" -amin +5 -delete -print"

DESTINATION_NUMBER=( $DESTINATION_NUMBER )

function gen_file() {
    SIP_DESTINATION_NUMBER=$1
    SIP_RECORDING=$2
    cat <<EOT >> /tmp/callalert/callfile/alert-${TIMESTAMP}-${SIP_DESTINATION_NUMBER}.call
Channel: SIP/${SIP_TRUNK}/${SIP_DESTINATION_NUMBER}
CallerID: ${SIP_CALLERID}
Application: Playback
Data: ${SIP_RECORDING}
EOT
}

for n in ${DESTINATION_NUMBER[@]}; do
    gen_file ${n} alert-${TIMESTAMP}
    scp -i ${SIP_SERVER_SSHKEY} /tmp/callalert/callfile/alert-${TIMESTAMP}-${n}.call root@${SIP_SERVER}:${SIP_CALLFILE_PATH}
done
