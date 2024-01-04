#!/bin/bash
TRIGGER_NAME="Aman is testing Alert"
TRIGGER_SEVERITY="High"

CALLALERT_URL="http://localhost:5080/callalert"

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

