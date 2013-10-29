#!/usr/bin/env python

import time
import datetime
import requests
import sys
import json
from urllib import urlencode

#Your PagerDuty API key.  A read-only key will work for this.
AUTH_TOKEN = 'YQstXoCv5Jsib56A6zeu'
#The API base url, make sure to include the subdomain
BASE_URL = 'https://pdt-ryan.pagerduty.com/api/v1'
#The service that you would like to get data on
service_id = "PFZ3ZG7"

HEADERS = {
    'Authorization': 'Token token={0}'.format(AUTH_TOKEN),
    'Content-type': 'application/json',
}

total_time = 0
total_ack_time = 0
incident_count = 0
escalation_count = 0
acked_count = 0

def get_service_name(service_id):
    params = {
        'service':service_id
    }
    services = requests.get(
        '{0}/services/{1}'.format(BASE_URL,service_id),
        headers=HEADERS,
        data=json.dumps(params)
    )
    return services.json()['service']['name']

def get_incident_count(service_id):
    global incident_count

    params = {
        'service':service_id,
        'date_range':'all'
    }
    count = requests.get(
        '{0}/incidents/count'.format(BASE_URL),
        headers=HEADERS,
        data=json.dumps(params)
    )
    incident_count = count.json()['total']

def get_incidents(service_id, offset):
    global total_time

    params = {
        'offset':offset,
        'limit':100,
        'service':service_id,
        'date_range':'all'
    }
    all_incidents = requests.get(
        '{0}/incidents'.format(BASE_URL),
        headers=HEADERS,
        data=json.dumps(params)
    )

    print "Listing all incidents:"
    for incident in all_incidents.json()['incidents']:
        print  "{0}:{1}".format(incident["incident_number"],incident["id"])
        get_incident_times(incident["id"])

def get_incident_times(incident_id):
    global total_time
    global total_ack_time
    global escalation_count
    global acked_count

    start_time = ""
    end_time = ""
    ack_time = ""

    params = {
        'is_overview: false'
    }
    log_entries = requests.get(
        '{0}/incidents/{1}/log_entries'.format(BASE_URL,incident_id),
        headers=HEADERS
    )

    for log_entry in log_entries.json()['log_entries']:
        if log_entry["type"] == "trigger":
            if log_entry["created_at"] > start_time:
                start_time = time.mktime(datetime.datetime.strptime(log_entry["created_at"],"%Y-%m-%dT%H:%M:%SZ").timetuple())
        elif log_entry["type"] == "resolve":
            end_time = time.mktime(datetime.datetime.strptime(log_entry["created_at"],"%Y-%m-%dT%H:%M:%SZ").timetuple())
        elif log_entry["type"] == "acknowledge":
            ack_time = time.mktime(datetime.datetime.strptime(log_entry["created_at"],"%Y-%m-%dT%H:%M:%SZ").timetuple())
        elif log_entry["type"] in ("escalate", "assign"):
            escalation_count = escalation_count + 1

    if end_time:
        elapsed_time = (end_time - start_time)/60
        total_time = total_time + elapsed_time
    if ack_time:
        ack_time = (ack_time - start_time)/60
        total_ack_time = total_ack_time + ack_time
        acked_count = acked_count + 1

print "Statistics for service: ", get_service_name(service_id)
get_incident_count(service_id)
print "Number of incidents: ", incident_count

for offset in xrange(0,incident_count):
    if offset % 100 == 0:
        get_incidents(service_id, offset)

print "Total unresolved incident time: %.2f minutes" % float(total_time)
if incident_count > 0:
    print "Average resolution time: %.2f minutes" % (float(total_time)/float(incident_count))
print "Total escalations: ", escalation_count - incident_count
if escalation_count - incident_count > 0:
    print "Average number of escalations: %.2f" % (float(escalation_count - incident_count)/float(incident_count))
print "Total acknowledgments: {0}".format(acked_count)
if acked_count > 0:
    print "Average acknowledgement time: {0} minutes".format(float(total_ack_time)/float(acked_count))
