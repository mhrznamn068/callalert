CALLALERT_URL="http://localhost:5000/callalert"
PROMETHUES_CALLALERT_URL="http://localhost:5000//callalert/prometheus"
TRIGGER_NAME="Test Alert"
TRIGGER_SEVERITY="High"
destination_number=""

generate_post_data()
{
  cat <<EOF
{
  "trigger_name": "$TRIGGER_NAME",
  "trigger_severity": "$TRIGGER_SEVERITY",
  "destination_number": "$destination_number"
}
EOF
}

curl -X POST $CALLALERT_URL \
  -H 'Content-Type: application/json' \
  --data-raw "$(generate_post_data)"
