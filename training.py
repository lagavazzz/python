#!/usr/bin/python3
from zabbix_utils import ZabbixAPI
from wonderwords import RandomWord
# Zabbix server details
zabbix_url = "https://student-XX-zbxtr-YYYY.zabbix.training"
api = ZabbixAPI(url=zabbix_url)
api.login(token="your-API-token")
# Initialize random word generator
rw = RandomWord()
def create_host(host_name):
    result = api.host.create({
        "host": host_name,
        "interfaces": [{
        "type": 1,
        "main": 1,
        "useip": 0,
        "ip": "",
        "dns": "training.example.com",
        "port": "10050"
    }],
    "groups": [{
        "groupid": "2"  #Linux servers
    }],
    "templates": [{
        "templateid": "10561"   # Zabbix agent
    }]
    })
    return result
# Generate and create 100 hosts with random names
for _ in range(100):
    word1 = rw.word()
    word2 = rw.word()
    host_name = f"{word1.capitalize()} {word2.capitalize()}"
    result = create_host(host_name)
    print(f"Created host: {host_name} - Result: {result}")
