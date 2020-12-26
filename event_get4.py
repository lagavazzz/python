#!/usr/bin/env python3.6

import re
import os
import sys
import time
import pprint
import logging
import logging.handlers
from datetime import datetime
from pyzabbix import ZabbixAPI
from requests.exceptions import ConnectionError

#enabling logging to system logs 
class SyslogBOMFormatter(logging.Formatter):
    def format(self, record):
        result = super().format(record)
        return "ufeff" + result
 
handler = logging.handlers.SysLogHandler('/dev/log')
formatter = SyslogBOMFormatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)

#pip install config
sys.path.insert(0,'/var/lib/zabbix/')
import config
ZABBIX_SERVER = config.url
zapi = ZabbixAPI(ZABBIX_SERVER)
try:
	connect = zapi.login(config.username, config.password)
except ConnectionError as conn_error:
        logging.exception(str(conn_error))

#Get timestamps from 30 days back
days = config.days
start_time = int(time.time()) - (3600 * 24 * int(days))

# get tagged problems
tag_name = config.tag_name
tag_value = config.tag_value
tagged_problems=zapi.problem.get(time_from = start_time, tags=[{'tag': tag_name, 'value': tag_value, 'operator': 0}], output = ['eventid'])
event_ids = [event['eventid'] for event in tagged_problems]
#close tagged problems
try:
	events_closed = zapi.event.acknowledge(eventids = event_ids, action = '1')
	time = int(start_time)
#logging output to system log
	logging.info ('Events older than ' + (datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')) + ' closed ' + str(events_closed))
except Exception as error:
    	logging.exception(str(error))
finally:
# Logout from Zabbix
	zapi.user.logout()
