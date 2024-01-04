#!/bin/bash
<<<<<<< HEAD
TRIGGER_NAME="Aman is testing Alert"
TRIGGER_SEVERITY="High"

CALLALERT_URL="http://localhost:5080/callalert"
=======
TRIGGER_NAME="Aman is testing Alert)"
TRIGGER_SEVERITY="High"

CALLALERT_URL="http://172.17.1.9:5080/callalert"
>>>>>>> django

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

