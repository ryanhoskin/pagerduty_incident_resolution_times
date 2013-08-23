#!/usr/bin/env python

import time
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
num_incidents = 0
total_time = 0

def get_incidents(service_id):
    all_incidents = requests.get(
        '{0}/incidents'.format(BASE_URL),
        headers=HEADERS
    )
    sys.stdout.write("Listing all incidents:\n")
    for incident in all_incidents.json()['incidents']:
        print "incident_id: " + incident["id"]
        get_incident_times(incident["id"])
    print "Number of incidents", num_incidents
    print "Total time: ", total_time
    print "Average resolution time: ", total_time/num_incidents/60, " minutes"

def get_incident_times(incident_id):
    global num_incidents
    global total_time
    start_time = ""
    end_time = ""

    num_incidents = num_incidents + 1

    params = {
        'is_overview': True
    }
    log_entries = requests.get(
        '{0}/incidents/{1}/log_entries'.format(BASE_URL,incident_id),
        headers=HEADERS
    )

    for log_entry in log_entries.json()['log_entries']:
        if log_entry["type"] == "trigger":
            if log_entry["created_at"] > start_time:
                start_time = log_entry["created_at"]
                start_time2 = time.mktime(datetime.datetime.strptime(start_time,"%Y-%m-%dT%H:%M:%SZ").timetuple())
        elif log_entry["type"] == "resolve":
            end_time = log_entry["created_at"]
            end_time2 = time.mktime(datetime.datetime.strptime(end_time,"%Y-%m-%dT%H:%M:%SZ").timetuple())

    print "start_time: " + start_time
    print "end_time: " + end_time
    elapsed_time = (end_time2 - start_time2)/60
    print "elapsed_time: ", elapsed_time, " minutes"
    total_time = total_time + elapsed_time

service_id = "PUBX1JL"
get_incidents(service_id)