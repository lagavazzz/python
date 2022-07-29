#!/usr/bin/python3

###########################################
# start fix.sh and not this script directly
###########################################

from pyzabbix import ZabbixAPI
import csv
import os
import getpass
import logging
import sys

"""
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
log = logging.getLogger('pyzabbix')
log.addHandler(stream)
log.setLevel(logging.DEBUG)
"""

zapi = ZabbixAPI("https://myzabbixurl")
zapi.login("api", "xxxxxxxxx")
# print("Connected to Zabbix API Version %s" % zapi.api_version())

arg = sys.argv[1]
hosts = zapi.host.get(filter={"host": arg})

if (hosts == []) :
    print('#######################################')
    print(arg, '- Error: Host does not exist, exit')
    sys.exit() 

for host in hosts:
    host_id = host["hostid"]
    print('#######################################')
    print('# Host:', arg)
    print('# Hostid:', host_id)

try:

    # get main (main=1) snmp interface (type=2)
    interface = zapi.hostinterface.get(hostids=host_id,filter={"main":"1","type":"2"})
    
    # exit if no snmp interface exists
    if (interface == [] ) :
        print(arg, "Error: no snmp interface present, exit")
        sys.exit()

    # log some values
    interface_id = interface[0]["interfaceid"]
    print("# Interface_id:", interface_id)
    interface_ip = interface[0]["ip"]
    print("# Interface_ip:", interface_ip)

    # get NOT main (main=0) snmp interface (type=2) 
    interface_notmain = zapi.hostinterface.get(hostids=host_id,filter={"main":"0","type":"2"})

    # exit if no additional interface exists
    if (interface_notmain == [] ) :
        print(arg, "- Error: no additional snmp interface present, exit")
        sys.exit() 

    # interface_id_notmain
    interface_id_notmain = interface_notmain[0]["interfaceid"]
    print("# Interface_id_notmain:", interface_id_notmain)
    interface_ip_notmain = interface_notmain[0]["ip"]
    print("# Interface_ip_notmain:", interface_ip_notmain)
    print("# Interface:", interface)
    print("# Interface_notmain:", interface_notmain)
    print('#######################################')
    
    if not (interface_ip == interface_ip_notmain ): 
        print(arg, "- Warning: interfaces differ, main:", interface_ip, "notmain:", interface_ip_notmain)

    # get snmp items (type=20) for hostid
    items = zapi.item.get(hostids=host_id,output=["itemid","interfaceid","name"],filter={"type":"20"})
    # print("items:", items)

    for item in items:
        item_id = item["itemid"]
        iface_id = item["interfaceid"]
        item_name = item["name"]
        if ( iface_id == interface_id_notmain ):
            try:
                # update item with correct interface
                zapi.item.update(itemid=item_id,interfaceid=interface_id)
                print (arg,"- update: item", item_id, item_name, "to interface_id", interface_id)

            except:
                # write error
                print(arg, "- Error: Item can't be updated, might be discovered item:", item_id, item_name)
        else:
            print (arg, "- ok: item", item_id, item_name)


    # get snmp discovery rules for hostid
    lld_ids = zapi.discoveryrule.get(hostids=host_id,output=["itemid","interfaceid","name"],filter={"type":"20"})
    
    # walk through the loop 
    for lld_rule in lld_ids:
        lld_id = lld_rule["itemid"]
        lld_name = lld_rule["name"]
        # list of snmp prototypes
        prototypeids = zapi.itemprototype.get(discoveryids=lld_id,output=["itemid","interfaceid","name"])
        for iprototype in prototypeids:
            proto_id = iprototype["itemid"]
            proto_name = iprototype["name"]
            # update the interface to the correct one
            if ( iprototype["interfaceid"] == interface_id_notmain ) :
                update_prototype = zapi.itemprototype.update(itemid=proto_id,interfaceid=interface_id)
                print (arg, '- update: item prototype', proto_id, proto_name)
            # or do nothing if the interface is correct
            else:
                print (arg, "- ok: item prototype", proto_id, proto_name)
        # change also lld_rule interface if needed        
        if ( lld_rule["interfaceid"] == interface_id_notmain ):
            update_lld = zapi.discoveryrule.update(itemid=lld_id,interfaceid=interface_id)
            print (arg, "- update: discovery rule", lld_id, lld_name, "to interface_id", interface_id)

except Exception as error:

    logging.exception(str(error))

try:
    # delete the second (not main) interface
    zapi.do_request('hostinterface.delete', [interface_id_notmain])
    print (arg, "- Fixed: delete host interface:", interface_id_notmain)

except Exception as error:
    print (arg, "- Error: cannot delete interface because items might still be linked")

# Logout from Zabbix
zapi.user.logout()
