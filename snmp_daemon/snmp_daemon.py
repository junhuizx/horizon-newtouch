import netsnmp
import requests
import threading
import time
import json

from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient import client

BASE_API_URL = 'http://localhost'

AUTH_URL = 'http://localhost:5000/v2.0/'
USERNAME = 'admin'
PASSWORD = 'admin'
PROJECT_ID = 'admin'

## SNMP OID
# System Group
SYS = ".1.3.6.1.2.1.1"
SYS_DESCR = ".1.3.6.1.2.1.1.1"
SYS_OBJECT_ID = ".1.3.6.1.2.1.1.2"
SYS_UPTIME = ".1.3.6.1.2.1.1.3"
SYS_CONTACT = ".1.3.6.1.2.1.1.4"
SYS_NAME = ".1.3.6.1.2.1.1.5"
SYS_LOCATION = ".1.3.6.1.2.1.1.6"

HR_SW_RUNNAME = ".1.3.6.1.2.1.25.4.2.1.2"
HR_SW_RUNPARM = ".1.3.6.1.2.1.25.4.2.1.5"
# Interfaces Group
# CPU Group
CPU = ".1.3.6.1.4.1.2021.11"
USER_CPU = ".1.3.6.1.4.1.2021.11.9"
SYSTEM_CPU = ".1.3.6.1.4.1.2021.11.10"
IDLE_CPU = ".1.3.6.1.4.1.2021.11.11"
RAW_USER_CPU = ".1.3.6.1.4.1.2021.11.50"
RAW_NICE_CPU = ".1.3.6.1.4.1.2021.11.51"
RAW_SYSTEM_CPU = ".1.3.6.1.4.1.2021.11.52"
RAW_IDLE_CPU = ".1.3.6.1.4.1.2021.11.53"
# Memery Group
RAM = ".1.3.6.1.4.1.2021.4"
TOTAL_RAM = ".1.3.6.1.4.1.2021.4.5"
TOTAL_RAM_USED = ".1.3.6.1.4.1.2021.4.6"
TOTAL_RAM_FREE = ".1.3.6.1.4.1.2021.4.7"
# Disk Group
DISK = ".1.3.6.1.4.1.2021.9.1"
TOTAL_DISK = ".1.3.6.1.4.1.2021.9.1.6"
DISK_AVAIL = ".1.3.6.1.4.1.2021.9.1.7"
DISK_USED = ".1.3.6.1.4.1.2021.9.1.8"

def time2str(time):
    msecond = time % 100
    seconds = time / 100
    day = seconds / (3600 * 24)
    hour = (seconds - (3600 * 24) * day )/ 3600
    min = (seconds - (3600 * 24) * day - 3600 * hour) / 60
    second = seconds - (3600 * 24) * day - 3600 * hour - 60 * min

    return ("%d day %02d:%02d:%02d.%02d") %(day ,hour, min, second, msecond)

class Server(object):
    id = None
    name = None
    ip = None
    snmp_commit = None
    snmp_version = None
    services = None
    cpu_message = None

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.name = kwargs['name']
        self.ip = kwargs['ip']
        self.snmp_commit = kwargs['snmp_commit']
        self.snmp_version = kwargs['snmp_version']
        self.services = kwargs['services']
        self.session = netsnmp.Session(DestHost=self.ip, Version=2, Community=self.snmp_commit)

    def get_server_services(self):
        headers = {'content-type': 'application/json'}
        monitor_services = []
        for service in self.services:
            url = BASE_API_URL + str(service)
            re = requests.get(url, headers=headers)
	    #print re.text
            object = json.loads(re.text)
            monitor_services.append(str(object['name']))

        return monitor_services


    def get_snmp_sys_message(self):
        vars = netsnmp.VarList(netsnmp.Varbind(SYS))
        self.sys_message = self.session.walk(vars)

        self.sys_uptime = int(self.sys_message[2])
        self.sys_contact = self.sys_message[3]
        self.sys_name = self.sys_message[4]
        self.sys_location = self.sys_message[5]

    def get_snmp_cpu_message(self):
        vars = netsnmp.VarList(netsnmp.Varbind(CPU))
        self.cpu_message = self.session.walk(vars)

        self.cpu_usage = 100 - int(self.cpu_message[10])

    def get_snmp_mem_message(self):
        vars = netsnmp.VarList(netsnmp.Varbind(RAM))
        self.mem_message = self.session.walk(vars)

        self.total_ram = int(self.mem_message[4])
        self.total_ram_used = int(self.mem_message[5])
        self.total_ram_free = int(self.mem_message[6])

        self.ram_usage = "%.2f" % (100.00 - self.total_ram_used * 100.00 / self.total_ram)

    def get_snmp_disk_message(self):
        vars = netsnmp.VarList(netsnmp.Varbind(DISK))
        self.disk_message = self.session.walk(vars)

        self.total_disk = int(self.disk_message[5])
        self.total_avail_disk = int(self.disk_message[6])
        self.total_used_disk = int(self.disk_message[7])

        self.disk_usage = "%.2f" % (self.total_used_disk * 100.00 / self.total_disk)

    def get_snmp_process_messages(self):
        monitor_services = self.get_server_services()

        vars = netsnmp.VarList(netsnmp.Varbind(HR_SW_RUNNAME))
        self.process_name_message = self.session.walk(vars)


        vars = netsnmp.VarList(netsnmp.Varbind(HR_SW_RUNPARM))
        self.process_parm_message = self.session.walk(vars)

        self.process_num = len(self.process_name_message)

        self.process_message = []
        nvs = zip(self.process_name_message, self.process_parm_message)
        # self.process_message = [name + " " + parm for name,parm in nvs if None != parm]
        for name,parm in nvs:
            if None != parm:
                process = name + " " + parm
            else:
                process = name
            self.process_message.append(process)

        service_stats = []
        service_status_tmp = 0

        for service in monitor_services:
            for process in self.process_message:
                if service in process:
                    service_status_tmp = 1
                    break
            service_stats.append(service_status_tmp)
            service_status_tmp = 0

        nvs2 = zip(monitor_services, service_stats)
        self.service_status = dict((service, status) for service, status in nvs2)

    def get_snmp_message(self):
        self.get_snmp_sys_message()
        self.get_snmp_cpu_message()
        self.get_snmp_mem_message()
        self.get_snmp_disk_message()
        self.get_snmp_process_messages()

    def post_snmp_messgae(self):
        server = "/dashboard/api/v1/server/%s/" % (self.id)

        url = BASE_API_URL + "/dashboard/api/v1/server_monitor/"
        headers = {'content-type': 'application/json','X-HTTP-Method-Override': 'POST'}
        data = {"server": server,
                "cpu_usage": self.cpu_usage,
                "mem_usage": self.ram_usage,
                "disk_usage": self.disk_usage,
                "process_num": self.process_num,
                "process_status": self.service_status}

        re = requests.post(url, headers=headers, data=json.dumps(data))

        return re.text


def current_hypervisors_list():
    url = BASE_API_URL + "/dashboard/api/v1/server/"
    headers = {'content-type': 'application/json'}

    re = requests.get(url, headers=headers)

    object = json.loads(re.text)

    return object

def add_new_hypervisor(hypervisor):
    url = BASE_API_URL + "/dashboard/api/v1/server/"
    headers = {'content-type': 'application/json','X-HTTP-Method-Override': 'POST'}
    data = {"name": hypervisor.hypervisor_hostname,
            "ip": hypervisor.host_ip,
            "snmp_version": "2c",
            "snmp_commit": "newtouch",
            "services":""}

    re = requests.post(url, headers=headers, data=json.dumps(data))
    return re

def get_hypervisors_list():
    server_list = []

    auth = v2.Password(auth_url=AUTH_URL,
                   username=USERNAME,
                   password=PASSWORD,
                   tenant_name=PROJECT_ID)
    sess = session.Session(auth=auth)
    nova = client.Client('1.1', session=sess)

    try:
        hypervisors =  nova.hypervisors.list()
    except Exception:
        pass

    current_hypervisors = current_hypervisors_list()
    current_hypervisor_ip_list = []

    for current_hypervisor in current_hypervisors['objects']:
        current_hypervisor_ip_list.append(current_hypervisor['ip'])

    for hypervisor in hypervisors:
        if hypervisor.host_ip not in current_hypervisor_ip_list:
            add_new_hypervisor(hypervisor)

    current_hypervisors = current_hypervisors_list()
    for current_hypervisor in current_hypervisors['objects']:
        server = Server(id = current_hypervisor['id'],
                        name=current_hypervisor['name'],
                        ip=current_hypervisor['ip'],
                        snmp_commit=current_hypervisor['snmp_commit'],
                        snmp_version=current_hypervisor['snmp_version'],
                        services = current_hypervisor['services'])
        server_list.append(server)

    return server_list

if __name__ == "__main__":
    server_list = get_hypervisors_list()
    count = 2
    while True:
        if 0 == count:
            print '==================================='
            server_list = get_hypervisors_list()
            count = 2

        for server in server_list:
	    try:
            	print "Get SNMP message from %s(%s)" % (server.name, server.ip)
            	server.get_snmp_message()
            	server.post_snmp_messgae()
    	    except Exception:
		pass

        count -= 1
        time.sleep(150)

