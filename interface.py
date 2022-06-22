#!/usr/bin/python3

from pyzabbix import ZabbixAPI
import csv
import os
import getpass
import sys


zapi = ZabbixAPI("http://127.0.0.1/zabbix")
zapi.login("Admin", "zabbix")
print("Connected to Zabbix API Version %s" % zapi.api_version())

arg = sys.argv[1]

hosts = zapi.host.get(filter={"host": arg})

if hosts:
        host_id = hosts[0]["hostid"]

print("Found host id {0}".format(host_id))

try:

    interface = zapi.hostinterface.get(hostids=host_id,output="extend",filter={"main":"1"})
    interface_id = interface[0]["interfaceid"]
    items = zapi.item.get(hostids=host_id,output=["itemid","type"])

    for item in items:
          item_id = item["itemid"]
          type = item["type"]
          if (type == "20"):
                  updateitem = zapi.item.update(itemid=item_id,interfaceid=interface_id)
                  print ('Interface updated for ' + str(updateitem))
          else:
                  print('Not an SNMP item' + str(item_id))

except Exception as error:

    logging.exception(str(error))

finally:


# Logout from Zabbix

    zapi.user.logout()
