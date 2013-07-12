#!/usr/bin/env python

import datetime
import requests
import sys
from urllib import urlencode

#Your PagerDuty API key.  A read-only key will work for this.
AUTH_TOKEN = 'mRw3SBLy6WxD4qVsJiGB'
#The API base url, make sure to include the subdomain
BASE_URL = 'https://pdt-ryan.pagerduty.com/api/v1'

HEADERS = {
    'Authorization': 'Token token={0}'.format(AUTH_TOKEN),
    'Content-type': 'application/json',
}

def get_incidents(service_id):
    all_incidents = requests.get(
        '{0}/incidents'.format(BASE_URL),
        headers=HEADERS
    )
    sys.stdout.write("Listing all incidents:\n")
    for incident in all_incidents.json()['incidents']:
        sys.stdout.write("Incident ID:")
        sys.stdout.write(incident["id"])
        sys.stdout.write("\n")
        get_incident_start_times(incident["id"])

def get_incident_start_times(incident_id):
    params = {
        'is_overview: true',
    }
    log_entries = requests.get(
        '{0}/incidents/{1}/log_entries'.format(BASE_URL,incident_id),
        headers=HEADERS
    )
    sys.stdout.write("Log Entries:\n")
    start_time = ""
    end_time = ""
    for log_entry in log_entries.json()['log_entries']:
        if log_entry["type"] == "trigger":
            if log_entry["created_at"] > start_time:
                start_time = log_entry["created_at"]
        elif log_entry["type"] == "resolve":
            end_time = log_entry["created_at"]
    sys.stdout.write("start_time:")
    sys.stdout.write(start_time)
    sys.stdout.write("\n")
    sys.stdout.write("end_time")
    sys.stdout.write(end_time)
    sys.stdout.write("\n")
    total_time = end_time - start_time
    sys.stdout.write("Total Time:")
    sys.stdout.write(total_time)
    sys.stdout.write("\n")

service_id = "PUBX1JL"
get_incidents(service_id)