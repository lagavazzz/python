#!/usr/bin/python3

from pyzabbix import ZabbixAPI
import csv
import os
import getpass


zapi = ZabbixAPI("http://127.0.0.1/zabbix")
zapi.login("Admin", "zabbix")
print("Connected to Zabbix API Version %s" % zapi.api_version())

import sys

arg = sys.argv[1]
#input_file = open("test.txt". "r")
#arg = str(input_file.readline())

hosts = zapi.host.get(filter={"host": arg})

if hosts:
        host_id = hosts[0]["hostid"]

lldids = zapi.discoveryrule.get(hostids=host_id,output=["itemid"])

if lldids:
       lldid = lldids[0]["itemid"]

print("Found host id {0}".format(host_id))

try:

    interface = zapi.hostinterface.get(hostids=host_id,output="extend",filter={"main":"1","type":"2"})
    interface_id = interface[0]["interfaceid"]
    items = zapi.item.get(hostids=host_id,output=["itemid","type"],filter={"type":"20"})
    lldruleid = zapi.discoveryrule.get(hostids=host_id,output=["itemid"])
    prototypeids = zapi.itemprototype.get(discoveryids=lldid,output=["itemid","type"],filter={"type":"20"})
    lldrules = zapi.discoveryrule.get(hostids=host_id,output=["itemid","type"],filter={"type":"20"})

    for item in items:
          item_id = item["itemid"]
          type = item["type"]
          if (type == "20"):
                  updateitem = zapi.item.update(itemid=item_id,interfaceid=interface_id)
                  print ('Interface updated for item' + str(updateitem))
    for lldrule in lldrules:
          lld_id = lldrule["itemid"]
          lldrule_type = lldrule["type"]
          if (type == "20"):
                  updatelld = zapi.discoveryrule.update(itemid=lld_id,interfaceid=interface_id)
                  print ('Interface updated for discovery rule' + str(updatelld))
    for iprototype in prototypeids:
          proto_id = iprototype["itemid"]
          proto_type = iprototype["type"]
          if (type == "20"):
                  updatelld = zapi.itemprototype.update(itemid=proto_id,interfaceid=interface_id)
                  print ('Interface updated for item prototype' + str(updatelld))
          else:
                  print('Not an SNMP item' + str(lld_id))

except Exception as error:

    logging.exception(str(error))

finally:


# Logout from Zabbix

    zapi.user.logout()
