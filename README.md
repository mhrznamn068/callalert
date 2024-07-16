# callalert

## Zabbix Action

### Run
```
docker-compose up -d
```

### Generate Alert 
#### Bash
```
#!/bin/bash
TRIGGER_NAME="Test Alert"
TRIGGER_SEVERITY="High"

CALLALERT_URL="http://127.0.0.1:5080/callalert"

generate_post_data()
{
  cat <<EOF
{
  "trigger_name": "$TRIGGER_NAME",
  "trigger_severity": "$TRIGGER_SEVERITY",
  "destination_number": "980xxxxxxx,980xxxxxxxx,980xxxxxxxx"
}
EOF
}

curl -X POST $CALLALERT_URL \
  -H 'Content-Type: application/json' \
  --data-raw "$(generate_post_data)"
```
#### Python
```
def callalert(trigger_name, trigger_severity, destination_number):
    CALLALERT_URL = os.environ.get("CALLALERT_URL")

    def generate_post_data():
        return {
            "trigger_name": trigger_name,
            "trigger_severity": trigger_severity,
            "destination_number": destination_number
        }

    response = requests.post(CALLALERT_URL, headers={'Content-Type': 'application/json'}, json=generate_post_data())
    return response.text

TRIGGER_NAME = "Test Alert"
TRIGGER_SEVERITY = "High"
DESTINATION_NUMBER = "980xxxxxxx,980xxxxxxxx,980xxxxxxxx"
callalert(TRIGGER_NAME, TRIGGER_SEVERITY, DESTINATION_NUMBER)
```
