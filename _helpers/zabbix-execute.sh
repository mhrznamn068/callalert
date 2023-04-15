#!/bin/bash

[ -d "/tmp/alertcall/soundtext" ] && echo "Directory /tmp/alertcall/soundtext exists." || mkdir -p /tmp/alertcall/soundtext
find /tmp/alertcall -mtime +1 -delete -print

cat <<EOT > /tmp/alertcall/soundtext/alert.txt
{TRIGGER.NAME}
{TRIGGER.SEVERITY}
EOT

TRIGGER_NAME=$(sed -n '1p' /tmp/alertcall/soundtext/alert.txt)
TRIGGER_SEVERITY=$(sed -n '2p' /tmp/alertcall/soundtext/alert.txt)

CALLALERT_URL=""

generate_post_data()
{
  cat <<EOF
{
  "trigger_name": "$TRIGGER_NAME",
  "trigger_severity": "$TRIGGER_SEVERITY"
}
EOF
}

curl -X POST $CALLALERT_URL \
  -H 'Content-Type: application/json' \
  --data-raw "$(generate_post_data)"
