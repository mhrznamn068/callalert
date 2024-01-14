from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .recordgen import gen_recording
from .helpers import workdir_init, upload_recording, upload_callfile, callfile
from .models import *
import json
from datetime import datetime
from pathlib import Path
import arrow
import logging

ORG_NAME = settings.ORG_NAME

def get_mobile_numbers(group_name):
    try:
        escalation_group = get_object_or_404(EscalationUserGroup, name=group_name)
        user_profiles = UserProfile.objects.filter(escalation_user_group=escalation_group)
        mobile_numbers = [profile.mobile_number for profile in user_profiles if profile.mobile_number]
        return mobile_numbers
    except EscalationUserGroup.DoesNotExist:
        return None

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
    
    trigger_name = data.get("trigger_name")
    trigger_severity = data.get("trigger_severity")
    call_destination_group = data.get("call_destination_group")
    destination_numbers = get_mobile_numbers(call_destination_group)

    timestamp = workdir_init()[0]
    work_dir_parent = workdir_init()[1]

    alert_text = f"{settings.ORG_NAME} System Alert, Attention Required, {trigger_name} alert triggered, {trigger_severity} Severity"

    f = open(f"{work_dir_parent}/soundtext/alert-{timestamp}.txt", "w")
    f.write(alert_text)
    f.close()

    gen_recording(timestamp, trigger_name, trigger_severity)
    upload_recording(work_dir_parent, timestamp)

    response_data = []

    if destination_numbers is not None:
        for number in destination_numbers:
            try:
                user_profile = UserProfile.objects.get(mobile_number=number)
                current_user = user_profile.user
            except UserProfile.DoesNotExist:
                logging.error(f"UserProfile not found for mobile number: {number}")
                response_data.append({"status": False, "message": f"User {current_user} not found."})
                continue

            if call_destination_group == "SRE":
                try:
                  on_call_duty = OnCallDuty.objects.get(user=current_user)
                except OnCallDuty.DoesNotExist:
                    logging.error(f"OnCallDuty instance not found for user: {current_user.username}")
                    response_data.append({"status": False, "message": f"User {current_user} is not on duty."})
                    continue
                if on_call_duty.duty:
                    callfile(work_dir_parent, timestamp, number)
                    upload_callfile(work_dir_parent, timestamp, number)
                    # Save alert history to the database
                    alerthistory.objects.create(
                        trigger_name=f'{timestamp}-{trigger_name}',
                        trigger_severity=trigger_severity,
                        destination_number=",".join(destination_numbers),
                        call_source=request.resolver_match.url_name,
                    )
                    response_data.append({"status": True, "message": f"User {current_user} is on duty, Sending Call Alerts"})
                else:
                    response_data.append({"status": False, "message": f"User {current_user} is not on duty."})
            else:
                callfile(work_dir_parent, timestamp, number)
                upload_callfile(work_dir_parent, timestamp, number)
                alerthistory.objects.create(
                    trigger_name=f'{timestamp}-{trigger_name}',
                    trigger_severity=trigger_severity,
                    destination_number=",".join(destination_numbers),
                    call_source=request.resolver_match.url_name,
                )
                response_data.append({"status": True, "message": f"User {current_user}, Sending Call Alerts"})

    return JsonResponse(
        {
            "status": True,
            "message": f"Call Alert Successful - Call Message: {alert_text} - Destination Number: {number}",
        }
    )

@csrf_exempt
@require_POST
def zabbix(request):
    if request.content_type != 'application/json':
        return HttpResponse('Invalid content-type. Must be application/json.', status=415)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON data.', status=400)
    
    trigger_name = data.get("trigger_name")
    trigger_severity = data.get("trigger_severity")
    call_destination_group = data.get("call_destination_group")
    destination_numbers = get_mobile_numbers(call_destination_group)

    timestamp = workdir_init()[0]
    work_dir_parent = workdir_init()[1]

    alert_text = f"{settings.ORG_NAME} System Alert, Attention Required, {trigger_name} alert triggered, {trigger_severity} Severity"

    f = open(f"{work_dir_parent}/soundtext/alert-{timestamp}.txt", "w")
    f.write(alert_text)
    f.close()

    gen_recording(timestamp, trigger_name, trigger_severity)
    upload_recording(work_dir_parent, timestamp)

    response_data = []

    if destination_numbers is not None:
        for number in destination_numbers:
            try:
                user_profile = UserProfile.objects.get(mobile_number=number)
                current_user = user_profile.user
            except UserProfile.DoesNotExist:
                logging.error(f"UserProfile not found for mobile number: {number}")
                response_data.append({"status": False, "message": f"User {current_user} not found."})
                continue
    
            try:
              on_call_duty = OnCallDuty.objects.get(user=current_user)
            except OnCallDuty.DoesNotExist:
                logging.error(f"OnCallDuty instance not found for user: {current_user.username}")
                response_data.append({"status": False, "message": f"User {current_user} is not on duty."})
                continue
    
            if on_call_duty.duty:
                callfile(work_dir_parent, timestamp, number)
                upload_callfile(work_dir_parent, timestamp, number)

                # Save alert history to the database
                alerthistory.objects.create(
                    trigger_name=f'{timestamp}-{trigger_name}',
                    trigger_severity=trigger_severity,
                    destination_number=",".join(destination_numbers),
                    #timestamp=timestamp,
                    call_source=request.resolver_match.url_name,
                )
                response_data.append({"status": True, "message": f"User {current_user} is on duty, Sending Call Alerts"})
            else:
                response_data.append({"status": False, "message": f"User {current_user} is not on duty."})

    return JsonResponse(
        {
            "status": True,
            "message": f"Call Alert Successful - Call Message: {alert_text} - Destination Number: {number}",
        }
    )

@csrf_exempt
@require_POST
def prometheus(request):
    if request.content_type != 'application/json':
        return HttpResponse('Invalid content-type. Must be application/json.', status=415)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON data.', status=400)

    timestamp = workdir_init()[0]
    work_dir_parent = workdir_init()[1]

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