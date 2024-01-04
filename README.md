# callalert

## Zabbix Action

### Run
```
docker-compose up -d
```

### Execute Command
```
#!/bin/bash
TRIGGER_NAME={TRIGGER.NAME}
TRIGGER_SEVERITY={TRIGGER.SEVERITY}

curl -X POST 'http://<server_ip>:<port>/callalert' -H 'Content-Type: application/json' --data-raw '{"trigger_name":$TRIGGER_NAME,"trigger_severity":$TRIGGER_SEVERITY}'
```
