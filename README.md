# callalert

### Run
```
docker-compose up -d
```

### Create Shifts
```
docker-compose run app bash
python manage.py loaddata callalert/fixtures/shifts.json
```

### Execute Command
```
#!/bin/bash
TRIGGER_NAME="Test Alert"
TRIGGER_SEVERITY="High"
DESTINATION_NUMBER="98xxxxxx"
curl -X POST 'http://localhost:4000/callalert/call/' -H 'Content-Type: application/json' --data-raw "{\"trigger_name\":\"$TRIGGER_NAME\",\"trigger_severity\":\"$TRIGGER_SEVERITY\",\"destination_number\":\"$DESTINATION_NUMBER\"}"

```