from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.conf import settings
from .recordgen import gen_recording
from .helpers import workdir_init, upload_recording, upload_callfile, callfile
from .models import alerthistory
import json
from datetime import datetime
from pathlib import Path
import arrow

ORG_NAME = settings.ORG_NAME

@csrf_exempt
@require_POST
def index(request):
    return HttpResponse("Welcome To Call Alert App")

@csrf_exempt
@require_POST
def call(request):
    if request.content_type != 'application/json':
        return HttpResponse('Invalid content-type. Must be application/json.', status=415)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON data.', status=400)

    timestamp = workdir_init()[0]
    work_dir_parent = workdir_init()[1]
    print(timestamp)
    print(work_dir_parent)

    trigger_name = data.get("trigger_name")
    trigger_severity = data.get("trigger_severity")
    destination_number = data.get("destination_number", "").split(',')

    alert_text = f"{settings.ORG_NAME} System Alert, Attention Required, {trigger_name} alert triggered, {trigger_severity} Severity"
    #print(alert_text)

    f = open(f"{work_dir_parent}/soundtext/alert-{timestamp}.txt", "w")
    f.write(alert_text)
    f.close()

    gen_recording(timestamp, trigger_name, trigger_severity)
    upload_recording(work_dir_parent, timestamp)

    for n in destination_number:
        callfile(work_dir_parent, timestamp, n)
        upload_callfile(work_dir_parent, timestamp, n)

    # Save alert history to the database
    alerthistory.objects.create(
        trigger_name=trigger_name,
        trigger_severity=trigger_severity,
        destination_number=','.join(destination_number),
    )

    return JsonResponse(
        {
            "status": True,
            "message": f"Call Alert Successful - Call Message: {alert_text}",
        }
    )

@csrf_exempt
@require_POST
def zabbix(request):
    if request.content_type != 'application/json':
        return HttpResponse('Invalid content-type. Must be application/json.', status=415)

    timestamp, work_dir_parent = workdir_init()
    data = request.json

    trigger_name = data["trigger_name"]
    trigger_severity = data["trigger_severity"]
    destination_number = data["destination_number"].split(',')

    alert_text = f"{ORG_NAME} System Alert, Attention Required, {trigger_name} alert triggered, {trigger_severity} Severity"
    print(alert_text)

    f = open(f"{work_dir_parent}/soundtext/alert-{timestamp}.txt", "w")
    f.write(alert_text)
    f.close()

    gen_recording(timestamp, trigger_name, trigger_severity)
    upload_recording(work_dir_parent, timestamp)

    for n in destination_number:
        callfile(work_dir_parent, timestamp, n)
        upload_callfile(work_dir_parent, timestamp, n)

    # Save alert history to the database
    alerthistory.objects.create(
        trigger_name=trigger_name,
        trigger_severity=trigger_severity,
        destination_number=','.join(destination_number),
    )

    return JsonResponse(
        {
            "status": True,
            "message": f"Call Alert Successful - Call Message: {alert_text}",
        }
    )

@csrf_exempt
@require_POST
def prometheus(request):
    if request.content_type != 'application/json':
        return HttpResponse('Invalid content-type. Must be application/json.', status=415)

    timestamp, work_dir_parent = workdir_init()
    data = request.json

    item_dict = data
    trigger_len = len(item_dict['alerts'])
    trigger_job = ""
    
    for n in range(trigger_len):
        trigger_name = item_dict["alerts"][n]["labels"]["alertname"]
        trigger_severity = item_dict["alerts"][n]["labels"]["severity"]
        trigger_job_item = item_dict["alerts"][n]["labels"]["job"]
        trigger_job = f'{trigger_job} and {trigger_job_item}' if trigger_job else trigger_job_item

    destination_number = data["destination_number"].split(',')

    alert_text = f"{ORG_NAME} System Alert, Attention Required, {trigger_name} alert triggered in {trigger_job}, {trigger_severity} Severity"
    print(alert_text)

    f = open(f"{work_dir_parent}/soundtext/alert-{timestamp}.txt", "w")
    f.write(alert_text)
    f.close()

    gen_recording(timestamp, trigger_name, trigger_severity)
    upload_recording(work_dir_parent, timestamp)

    for n in destination_number:
        callfile(work_dir_parent, timestamp, n)
        upload_callfile(work_dir_parent, timestamp, n)

    # Save alert history to the database
    alerthistory.objects.create(
        trigger_name=trigger_name,
        trigger_severity=trigger_severity,
        destination_number=','.join(destination_number),
    )

    return JsonResponse(
        {
            "status": True,
            "message": f"Call Alert Successful - Call Message: {alert_text}",
        }
    )