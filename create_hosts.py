#!/usr/bin/env python3
# import hosts from txt file to Zabbix via API
# and assign template and host group to them

# python3 required
# dnf install python3-pip
# pip3 install zabbix_api
# script is tested and works with module 'zabbix_api'
# which is not the same as 'pyzabbix' !
import csv

from zabbix_api import ZabbixAPI

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import sys
sys.path.insert(0,'/var/lib/zabbix')

# pip install config
import config
ZABBIX_SERVER = config.url
zapi = ZabbixAPI(ZABBIX_SERVER)
zapi.session.verify=False
zapi.login(config.username, config.password)

file = open("hostlist.csv",'rt')
reader = csv.DictReader( file )

# take the file and read line by line
for line in reader:
 
 # check if this host exists in zabbix
 if not zapi.host.get({"filter":{"host" :line['name']}}):
  print (line['name'],"not yet registred")
  if zapi.proxy.get({"output": "proxyid","selectInterface": "extend","filter":{"host":line['proxy']}}):
   proxy_id=zapi.proxy.get({"output": "proxyid","selectInterface": "extend","filter":{"host":line['proxy']}})[0]['proxyid']
   print (line['proxy'])
   if int(proxy_id)>0:
     templates=line['template'].split(";")
     groups=line['group'].split(";")
     # take first group from group array
     group_id = zapi.hostgroup.get({"filter" : {"name" : groups[0]}})[0]['groupid']
     # take first template from template array
     template_id = zapi.template.get({"filter" : {"name" : templates[0]}})[0]['templateid']
     # crete a host an put hostid instantly in the 'hostid' variable
     hostid = zapi.host.create ({
        "host":line['name'],"interfaces":[{"type":2,"dns":"","main":1,"ip": line['address'],"port": 161,"useip": 1,"details":{"version":"2","bulk":"1","community":"{$SNMP_COMMUNITY}"}}],
        "groups": [{ "groupid": group_id }],
        "proxy_hostid":proxy_id,
        "templates": [{ "templateid": template_id }]})['hostids']

     # add additional templates
     if len(templates)>1:
      # skip the first element in array
      for one_template in templates[1:]:
       try:
        tid=zapi.template.get({"filter" : {"name" : one_template}})[0]['templateid']
        if tid:
          # link new template
          try:
           nt=zapi.template.massadd({"templates":tid,"hosts":hostid})
          except Exception as nt:
           print ("template",one_template,"probably already linked")
        else:
          print ("Temnplate:",one_template,"does not exist")
       except Exception as tid:
        print("Temnplate:",one_template,"does not exist")

     # add additional groups
     if len(groups)>1:
      for one_hostgroup in groups[1:]:
       try:
        gid=zapi.hostgroup.get({"filter" : {"name" : one_hostgroup}})[0]['groupid']
        if gid:
          # link new hostgroup
          try:
           nhg=zapi.hostgroup.massadd({"groups":gid,"hosts":hostid})
          except Exception as nhg:
           print ("Hostgroup",one_hostgroup,"probably already linked")
        else:
          print ("Hostgroup",one_hostgroup,"does not exist")
       except Exception as gid:
        print ("Hostgroup",one_hostgroup,"does not exist")

  # if there are no proxy
  else:
   print ("proxy does not exist. creating with none")
   templates=line['template'].split(";")
   groups=line['group'].split(";")
   # take first group from group array
   group_id = zapi.hostgroup.get({"filter" : {"name" : groups[0]}})[0]['groupid']
   # take first template from template array
   template_id = zapi.template.get({"filter" : {"name" : templates[0]}})[0]['templateid']
   # crete a host an put hostid instantly in the 'hostid' variable
   hostid = zapi.host.create ({
      "host":line['name'],"interfaces":[{"type":2,"dns":"","main":1,"ip": line['address'],"port": 161,"useip": 1,"details":{"version":"2","bulk":"1","community":"{$SNMP_COMMUNITY}"}}],
      "groups": [{ "groupid": group_id }],
      "templates": [{ "templateid": template_id }]})['hostids']

   # add additional templates
   if len(templates)>1:
    # skip the first element in array
    for one_template in templates[1:]:
     try:
      tid=zapi.template.get({"filter" : {"name" : one_template}})[0]['templateid']
      if tid:
        # link new template
        try:
         nt=zapi.template.massadd({"templates":tid,"hosts":hostid})
        except Exception as nt:
         print ("template",one_template,"probably already linked")
      else:
        print ("Temnplate:",one_template,"does not exist")
     except Exception as tid:
      print("Temnplate:",one_template,"does not exist")

   # add additional groups
   if len(groups)>1:
    for one_hostgroup in groups[1:]:
     try:
      gid=zapi.hostgroup.get({"filter" : {"name" : one_hostgroup}})[0]['groupid']
      if gid:
        # link new hostgroup
        try:
         nhg=zapi.hostgroup.massadd({"groups":gid,"hosts":hostid})
        except Exception as nhg:
         print ("Hostgroup",one_hostgroup,"probably already linked")
      else:
        print ("Hostgroup",one_hostgroup,"does not exist")
     except Exception as gid:
      print ("Hostgroup",one_hostgroup,"does not exist")
   

 else:
   print (line['name'],"already exist")

file.close()
