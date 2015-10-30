# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import MySQLdb
import netsnmp
import telnetlib
from uuid import uuid4
from django.utils.translation import ugettext_lazy as _

from horizon.utils import functions as utils
from openstack_dashboard.api.nova import hypervisor_list


MYSQL_HOST = '192.168.164.129'
MYSQL_SYSLOG_DB_NAME = 'Syslog'
MYSQL_SYSLOG_DB_USER = 'rsyslog'
MYSQL_SYSLOG_DB_PASSWD = '123456'

MYSQL_MONITOR_DB_NAME = 'monitor'
MYSQL_MONITOR_DB_USER = 'monitor'
MYSQL_MONITOR_DB_PASSWD = '123456'

DestHostList = ["192.168.202.1"]
ifDescr = ".1.3.6.1.2.1.2.2.1.2"
ifType = ".1.3.6.1.2.1.2.2.1.3"
ifSpeed = ".1.3.6.1.2.1.2.2.1.5"
ifAdminStatus = ".1.3.6.1.2.1.2.2.1.7"
ifOperStatus = ".1.3.6.1.2.1.2.2.1.8"
hh3cEntityExtCpuUsage = ".1.3.6.1.4.1.25506.2.6.1.1.1.1.6"
hh3cEntityExtMemUsage = ".1.3.6.1.4.1.25506.2.6.1.1.1.1.8"
hh3cEntityExtTemperature = ".1.3.6.1.4.1.25506.2.6.1.1.1.1.12"
hh3cFWMaxConnNum = ".1.3.6.1.4.1.25506.2.88.1.1.1"
hh3cFWConnNumCurr = ".1.3.6.1.4.1.25506.2.88.1.2.1"

ifNumber = ".1.3.6.1.2.1.2.1"
ifInOctets=".1.3.6.1.2.1.2.2.1.10"
ifOutOctets=".1.3.6.1.2.1.2.2.1.16"
ifInDiscards=".1.3.6.1.2.1.2.2.1.13"
ifOutDiscards=".1.3.6.1.2.1.2.2.1.19"
ifInErrors=".1.3.6.1.2.1.2.2.1.14"
ifOutErrors=".1.3.6.1.2.1.2.2.1.20"

ipAdEntAddr=".1.3.6.1.2.1.4.20.1.1"
ipAdEntIndex=".1.3.6.1.2.1.4.20.1.2"



def get_net_equipment_snmpmsg(host, commit):
    snmpmsg = SnmpMessage()

    snmpmsg.cpu = netsnmp.snmpwalk(hh3cEntityExtCpuUsage,
                                         Version = 2,
                                         DestHost = host,
                                         Community = commit)

    snmpmsg.mem = netsnmp.snmpwalk(hh3cEntityExtMemUsage,
                                         Version = 2,
                                         DestHost = host,
                                         Community = commit)
    return snmpmsg

def get_equipment(id):
    monitordb = MySQLdb.connect(MYSQL_HOST,
                                MYSQL_MONITOR_DB_NAME,
                                MYSQL_MONITOR_DB_PASSWD,
                                MYSQL_MONITOR_DB_NAME)

    cursor = monitordb.cursor()
    row = cursor.execute("SELECT * FROM equipments WHERE id=%d" % (id))
    results = cursor.fetchmany(row)

    for equipment in results:
        equipmentdetail = Equipment(equipment[0], equipment[1],
                  equipment[2], equipment[3], "", "",
                  equipment[4], equipment[5])

    cursor.close()
    monitordb.close()

    return equipmentdetail

class SnmpMessage(object):
    def __init__(self):
        self.cpu = None
        self.mem = None

class Equipment(object):
    def __init__(self, id, name, type,
                 ip, cpu_usage, mem_usage,
                 descrition, status):
        self.id = id
        self.name = name
        self.type = _(type)
        self.ip = ip
        self.cpu_usage = cpu_usage + "%"
        self.mem_usage = mem_usage + "%"
        self.descrition = descrition
        self.status = status

    def __str__(self):
        return self.name

class EquipmentMonitor(object):
    id = None
    name = None
    temperature = None
    ip = None
    cpu_usage = None
    mem_usage = None
    max_connect_num = None
    cur_connect_num = None
    interface_num = None

    def __init__(self, id, name, ip):
        self.id = id
        self.name = name
        self.ip = ip

    def fill_snmp_data(self):
        self.temperature = netsnmp.snmpwalk(hh3cEntityExtTemperature,
                                            Version = 2,
                                            DestHost = self.ip,
                                            Community = "newtouch")[2] + ' C'
        self.cpu_usage = netsnmp.snmpwalk(hh3cEntityExtCpuUsage,
                                          Version = 2,
                                          DestHost = self.ip,
                                          Community = "newtouch")[2] + "%"

        self.mem_usage = netsnmp.snmpwalk(hh3cEntityExtMemUsage,
                                          Version = 2,
                                          DestHost = self.ip,
                                          Community = "newtouch")[2] + "%"
        self.max_connect_num = netsnmp.snmpwalk(hh3cFWMaxConnNum,
                                            Version = 2,
                                            DestHost = self.ip,
                                            Community = "newtouch")[0]
        self.cur_connect_num = netsnmp.snmpwalk(hh3cFWConnNumCurr,
                                            Version = 2,
                                            DestHost = self.ip,
                                            Community = "newtouch")[0]
        self.interface_num = netsnmp.snmpwalk(ifNumber,
                                            Version = 2,
                                            DestHost = self.ip,
                                            Community = "newtouch")[0]



def equipment_monitor_equipment_list(request = None, marker = None, paginate = False, addr = None):
    equipments = []

    monitordb = MySQLdb.connect(MYSQL_HOST,
                                MYSQL_MONITOR_DB_NAME,
                                MYSQL_MONITOR_DB_PASSWD,
                                MYSQL_MONITOR_DB_NAME)

    cursor = monitordb.cursor()
    row = cursor.execute("SELECT * FROM equipments")
    results = cursor.fetchmany(row)

    for result in results:
        equipment = EquipmentMonitor(result[0], result[1], result[3])
        equipment.fill_snmp_data()

        equipments.append(equipment)

    cursor.close()
    monitordb.close()

    return equipments


def network_monitor_equipment_list(request = None, marker = None, paginate = False, addr = None):
    equipments = []

    monitordb = MySQLdb.connect(MYSQL_HOST,
                                MYSQL_MONITOR_DB_NAME,
                                MYSQL_MONITOR_DB_PASSWD,
                                MYSQL_MONITOR_DB_NAME)

    cursor = monitordb.cursor()
    if addr:
        row = cursor.execute("SELECT * FROM equipments WHERE addr=\'%s\'" % (addr))
    else:
        row = cursor.execute("SELECT * FROM equipments")
    results = cursor.fetchmany(row)

    for equipment in results:
        snmpmsg = get_net_equipment_snmpmsg(equipment[3], "newtouch")
        equipments.append(Equipment(equipment[0],
                                    equipment[1],
                                    equipment[2],
                                    equipment[3],
                                    snmpmsg.cpu[2],
                                    snmpmsg.mem[2],
                                    equipment[4],
                                    equipment[5]))

    cursor.close()
    monitordb.close()

    return equipments


class InterFace(object):
    def __init__(self, id, index, name, desthost, status):
        self.id = id
        self.name = name
        self.index = index
        self.desthost = desthost
        if 'GigabitEthernet0/0' == name:
            self.description = "Management(192.168.0.1/255.255.255.0)"
        elif 'GigabitEthernet0/1' == name:
            self.description = "Untrust(58.247.8.188/255.255.255.248)"
        elif 'GigabitEthernet0/2' == name:
            self.description = "Trust(192.168.202.1/255.255.0.0)"
        else:
            self.description = '-'
        if '1' == status:
            self.status = _("Connected")
        elif '2' == status:
            self.status = _("Not Connected")
        else:
            self.status = _("Unknown")
    def fill_interface_ip(self):
        ip_index = netsnmp.snmpwalk(ipAdEntIndex,
                                 Version = 2,
                                 DestHost = self.desthost,
                                 Community = "newtouch")

        if str(self.index + 1) in ip_index:
            self.desthost = netsnmp.snmpwalk(ipAdEntAddr,
                                 Version = 2,
                                 DestHost = self.desthost,
                                 Community = "newtouch")[ip_index.index(str(self.index + 1))]
        else:
            self.desthost = "-"

def get_interface(request, id):
    interfaces = []
    equipment = get_equipment(int(id))

    interfaces_name = netsnmp.snmpwalk(ifDescr,
                                           Version = 2,
                                           DestHost = equipment.ip,
                                           Community = "newtouch")
    interfaces_status = netsnmp.snmpwalk(ifOperStatus,
                                             Version = 2,
                                             DestHost = equipment.ip,
                                             Community = "newtouch")

    for interface in interfaces_name:
        if (-1 == interface.find("NULL")) & (-1 == interface.find("Vlan")):
                tag, sep, id = interface.partition("/")
                interfaceid = tag + "-" + id
                one_interface = InterFace(interfaceid, interfaces_name.index(interface),
                                          interface,equipment.ip,
                                          interfaces_status[interfaces_name.index(interface)])
                one_interface.fill_interface_ip()
                interfaces.append(one_interface)

    return interfaces

class EquipmentMonitorInterFace(object):
    def __init__(self, id, name, status, ip):
        self.id = id
        self.name = name
        if '1' == status:
            self.status = _("Connected")
        elif '2' == status:
            self.status = _("Not Connected")
        else:
            self.status = _("Unknown")
        self.equipment_ip = ip

    def fill_snmp_data(self):
        self.inoctets = netsnmp.snmpwalk(ifInOctets,
                                         Version = 2,
                                         DestHost = self.equipment_ip,
                                         Community = "newtouch")[self.id]
        self.outoctets = netsnmp.snmpwalk(ifOutOctets,
                                          Version = 2,
                                          DestHost = self.equipment_ip,
                                          Community = "newtouch")[self.id]
        self.indiscards = netsnmp.snmpwalk(ifInDiscards,
                                           Version = 2,
                                           DestHost = self.equipment_ip,
                                           Community = "newtouch")[self.id]
        self.outdiscards = netsnmp.snmpwalk(ifOutDiscards,
                                            Version = 2,
                                            DestHost = self.equipment_ip,
                                            Community = "newtouch")[self.id]
        self.inerrors = netsnmp.snmpwalk(ifInErrors,
                                         Version = 2,
                                         DestHost = self.equipment_ip,
                                         Community = "newtouch")[self.id]
        self.outerrors = netsnmp.snmpwalk(ifOutErrors,
                                          Version = 2,
                                          DestHost = self.equipment_ip,
                                          Community = "newtouch")[self.id]

    def fill_interface_ip(self):
        ip_index = netsnmp.snmpwalk(ipAdEntIndex,
                                 Version = 2,
                                 DestHost = self.equipment_ip,
                                 Community = "newtouch")

        if str(self.id + 1) in ip_index:
            self.ip = netsnmp.snmpwalk(ipAdEntAddr,
                                 Version = 2,
                                 DestHost = self.equipment_ip,
                                 Community = "newtouch")[ip_index.index(str(self.id + 1))]
        else:
            self.ip = "-"

def equipment_monitor_interface_list(request, interface):
    interfaces = []
    id, sep , num = interface.partition("-")
    equipment = get_equipment(int(id))

    interfaces_name = netsnmp.snmpwalk(ifDescr,
                                           Version = 2,
                                           DestHost = equipment.ip,
                                           Community = "newtouch")

    interfaces_status = netsnmp.snmpwalk(ifOperStatus,
                                             Version = 2,
                                             DestHost = equipment.ip,
                                             Community = "newtouch")


    for name in interfaces_name:
        interface = EquipmentMonitorInterFace(interfaces_name.index(name),
                                              name,
                                              interfaces_status[interfaces_name.index(name)],
                                              equipment.ip)
        interface.fill_snmp_data()
        interface.fill_interface_ip()
        interfaces.append(interface)

    return interfaces

class Logs(object):
    def __init__(self, dict):
        self.id = dict['id']
        self.time = dict['time']
        self.type = dict['type']
        self.host = dict['host']
        if 0 == dict['priority']:
            self.priority = _("Emergency")
        elif 1 == dict['priority']:
            self.priority = _("Alert")
        elif 2 == dict['priority']:
            self.priority = _("Critical")
        elif 3 == dict['priority']:
            self.priority = _("Error")
        elif 4 == dict['priority']:
            self.priority = _("Warning")
        elif 5 == dict['priority']:
            self.priority = _("Notice")
        elif 6 == dict['priority']:
            self.priority = _("Informational")
        elif 7 == dict['priority']:
            self.priority = _("Debug")
        else:
            self.priority = None
        self.interface = dict['interface']
        self.src_ip = dict['src_ip']
        self.dev_type = dict['dev_type']
        self.dest_ip = dict['dest_ip']
        self.message = dict['message']

    def __str__(self):
        return "%s-%s-%s" % (self.time, self.type, self.priority)

def get_syslogs_from_db(limit = None, marker = None,
                        system_tag = None, interface = None,
                        filters = None):
    '''
    Get syslogs from mysql
    :param limit:
    :param marker:
    :param system_tag:
    :return:
    '''
    syslogs = []
    syslogdb = MySQLdb.connect(MYSQL_HOST,
                               MYSQL_SYSLOG_DB_USER,
                               MYSQL_SYSLOG_DB_PASSWD,
                               MYSQL_SYSLOG_DB_NAME)
    cursor = syslogdb.cursor()

    filter = ''
    if filters.has_key('time'):
        filter = 'AND ReceivedAt LIKE "%s%s%s" ' % ("%",filters['time'],"%")
    elif filters.has_key('id'):
        try:
            tmp = int(filters['id'])
            filter = 'AND ID = %s ' % (filters['id'])
        except ValueError:
            filter = 'AND ID = %s ' % ("0")
    elif filters.has_key('type'):
        filter = 'AND Message LIKE "%s%s%s" ' % ("%", filters['type'], "%")
    elif filters.has_key('priority'):
        filter = 'AND Priority LIKE "%s%s%s" ' % ("%", filters['priority'], "%")
    else:
        pass

    print

    interface_name = ""
    if interface:
        interface_detail = interface.split("-")
        interface_name = ' AND (Message LIKE %s%s%s%s%s OR Message NOT LIKE %s%s%s ) ' % ("'%", interface_detail[0], "/", interface_detail[1], "%'",
                                                                                         "'%", interface_detail[0],"%'")
    if marker:
        sql = "SELECT * FROM SystemEvents WHERE (SysLogTag = {0} AND ID < {1} {2} {3}) ORDER BY id DESC"
        row = cursor.execute(sql.format(system_tag, int(marker), interface_name, filter))
    else:
        sql = "SELECT * FROM SystemEvents WHERE (SysLogTag = {0} {1} {2}) order by id DESC"
        row = cursor.execute(sql.format(system_tag, interface_name, filter))


    if row:
        results = cursor.fetchmany(row)
        for syslog in results:
            tag, sep, message  = syslog[7].partition(":")

            if (-1 != tag.find("message repeated")):
                message = message.strip().lstrip("[").rstrip("]")
                tag, sep, message = message.partition(":")

            type = tag.strip().lstrip("%%10")
            type = type.split("/", 1)[0]
            message_list = message.split(";")
            dev_type_value = ""
            interface_type_value = ""
            srcip_type_value = ""
            destip_type_value = ""
            for message in message_list:
                if -1 != message.find("DEV_TYPE"):
                    tag, sep , dev_type_value = message.partition("=")
                    dev_type_value = dev_type_value.strip()
                elif -1 != message.find("atckType"):
                    tag, sep , atck_type_value = message.partition("=")
                    atck_type_value = atck_type_value.strip()
                elif -1 != message.find("rcvIfName"):
                    tag, sep , interface_type_value = message.partition("=")
                    interface_type_value = interface_type_value.strip()
                elif -1 != message.find("srcIPAddr"):
                    tag, sep , srcip_type_value = message.partition("=")
                    srcip_type_value = srcip_type_value.strip()
                elif -1 != message.find("srcMacAddr"):
                    tag, sep , srcmac_type_value = message.partition("=")
                    srcmac_type_value = srcmac_type_value.strip()
                elif -1 != message.find("destIPAddr"):
                    tag, sep , destip_type_value = message.partition("=")
                    destip_type_value = destip_type_value.strip()
                elif -1 != message.find("destMacAddr"):
                    tag, sep , destmac_type_value = message.partition("=")
                    destmac_type_value = destmac_type_value.strip()
                else:
                    pass

            syslog_dict = dict(id=syslog[0], time=syslog[2], priority=syslog[5], host=syslog[6], message=syslog[7],
                               type=type, dev_type=dev_type_value, interface=interface_type_value,
                               src_ip=srcip_type_value, dest_ip=destip_type_value)

            syslogs.append(Logs(syslog_dict))
            if limit == len(syslogs):
                break

    cursor.close()
    syslogdb.close()

    return (syslogs, row)

def get_filter_syslogs_from_db(limit = None,
                marker = None,
                opt = None):
    '''

    :param limit:
    :param marker:
    :param opt:
    :return:
    '''
    syslogs = []
    syslogdb = MySQLdb.connect(MYSQL_HOST,
                               MYSQL_SYSLOG_DB_USER,
                               MYSQL_SYSLOG_DB_PASSWD,
                               MYSQL_SYSLOG_DB_NAME)
    cursor = syslogdb.cursor()

    sql_filter = "SELECT * FROM SystemEvents WHERE "
    sql_filter_tag = ""
    sql_filter_priority = ""
    sql_filter_type = ""
    sql_filter_starttime = ""
    sql_filter_endtime = ""
    sql_filter_marker = ""
    for system_tag in opt.tag_list:
        if "" == sql_filter_tag:
            sql_filter_tag = "SysLogTag = \'%s\' " % (system_tag)
        else:
            sql_filter_tag += "OR SysLogTag = \'%s\' " % (system_tag)

    if opt.priority:
        if "Emergency" == opt.priority:
            sql_filter_priority = "AND Priority = 0 "
        elif "Alert" == opt.priority:
            sql_filter_priority = "AND Priority = 1 "
        elif "Critical" == opt.priority:
            sql_filter_priority = "AND Priority = 2 "
        elif "Error" == opt.priority:
            sql_filter_priority = "AND Priority = 3 "
        elif "Warning" == opt.priority:
            sql_filter_priority = "AND Priority = 4 "
        elif "Notice" == opt.priority:
            sql_filter_priority = "AND Priority = 5 "
        elif "Informational" == opt.priority:
            sql_filter_priority = "AND Priority = 6 "
        elif "Debug" == opt.priority:
            sql_filter_priority = "AND Priority = 7 "
        else:
            sql_filter_priority = ""

    if opt.attack_type:
        sql_filter_type = "AND Message LIKE \'%s%s%s\' " % ('%', opt.attack_type, '%')

    if opt.StartTime:
        sql_filter_starttime = "AND ReceivedAt >= \'%s 00:00:01\' " % (opt.StartTime)

    if opt.EndTime:
        sql_filter_endtime = "AND ReceivedAt <= \'%s 24:00:00\' " % (opt.EndTime)

    if marker:
        sql_filter_marker = "AND ID < %s ORDER BY id DESC" % (marker)

    sql_filter = sql_filter + sql_filter_tag + \
                 sql_filter_priority + sql_filter_type + \
                 sql_filter_starttime + sql_filter_endtime + \
                 sql_filter_marker

    row = cursor.execute(sql_filter)

    if row:
        results = cursor.fetchmany(row)
        for syslog in results:
            tag, sep, message  = syslog[7].partition(":")

            if (-1 != tag.find("message repeated")):
                message = message.strip().lstrip("[").rstrip("]")
                tag, sep, message = message.partition(":")

            type = tag.strip().lstrip("%%10")
            type = type.split("/", 1)[0]
            message_list = message.split(";")
            dev_type_value = ""
            interface_type_value = ""
            srcip_type_value = ""
            destip_type_value = ""
            for message in message_list:
                if -1 != message.find("DEV_TYPE"):
                    tag, sep , dev_type_value = message.partition("=")
                    dev_type_value = dev_type_value.strip()
                elif -1 != message.find("atckType"):
                    tag, sep , atck_type_value = message.partition("=")
                    atck_type_value = atck_type_value.strip()
                elif -1 != message.find("rcvIfName"):
                    tag, sep , interface_type_value = message.partition("=")
                    interface_type_value = interface_type_value.strip()
                elif -1 != message.find("srcIPAddr"):
                    tag, sep , srcip_type_value = message.partition("=")
                    srcip_type_value = srcip_type_value.strip()
                elif -1 != message.find("srcMacAddr"):
                    tag, sep , srcmac_type_value = message.partition("=")
                    srcmac_type_value = srcmac_type_value.strip()
                elif -1 != message.find("destIPAddr"):
                    tag, sep , destip_type_value = message.partition("=")
                    destip_type_value = destip_type_value.strip()
                elif -1 != message.find("destMacAddr"):
                    tag, sep , destmac_type_value = message.partition("=")
                    destmac_type_value = destmac_type_value.strip()
                else:
                    pass

            syslog_dict = dict(id=syslog[0], time=syslog[2], priority=syslog[5], host=syslog[6], message=syslog[7],
                               type=type, dev_type=dev_type_value, interface=interface_type_value,
                               src_ip=srcip_type_value, dest_ip=destip_type_value)

            syslogs.append(Logs(syslog_dict))
            if limit == len(syslogs):
                break

    cursor.close()
    syslogdb.close()

    return (syslogs, row)

def syslog_list(request, marker = None,
                paginate = False, interface = None,
                filters = None):
    '''
    :return:syslog class list
    '''
    limit = 200
    page_size = utils.get_page_size(request)

    if paginate:
        request_size = page_size + 1
    else:
        request_size = limit

    syslogs, count = get_syslogs_from_db(limit=request_size,
                                         marker = marker,
                                         system_tag="\'Newtouch-H3C\'" ,
                                         interface = interface,
                                         filters = filters)
    # has_prev_data = False
    has_more_data = False
    if paginate:
        # images = list(itertools.islice(images_iter, request_size))
        # first and middle page condition
        if len(syslogs) > page_size:
            syslogs.pop(-1)
            has_more_data = True
            # middle page condition
            if marker is not None:
                pass
                # has_prev_data = True
        # last page condition
        elif marker is not None:
            pass
            # has_prev_data = True

    return (syslogs, has_more_data, count)

def filter_syslog_list(request,
              marker = None,
              paginate = False,
              opt = None):
    limit = 500
    page_size = utils.get_page_size(request)

    if paginate:
        request_size = page_size + 1
    else:
        request_size = limit

    syslogs, count = get_filter_syslogs_from_db(limit=request_size,
                          marker = marker,
                          opt = opt)
    # has_prev_data = False
    has_more_data = False
    if paginate:
        # images = list(itertools.islice(images_iter, request_size))
        # first and middle page condition
        if len(syslogs) > page_size:
            syslogs.pop(-1)
            has_more_data = True
            # middle page condition
            if marker is not None:
                pass
                # has_prev_data = True
        # last page condition
        elif marker is not None:
            pass
            # has_prev_data = True

    return (syslogs, has_more_data, count)

class LogDetail(object):
    def __init__(self, id, message):
        self.id = id
        self.message = message

def logs_detail(request, id):
    message = []
    syslogdb = MySQLdb.connect(MYSQL_HOST,MYSQL_SYSLOG_DB_USER,
                               MYSQL_SYSLOG_DB_PASSWD,MYSQL_SYSLOG_DB_NAME)
    cursor = syslogdb.cursor()
    sql = "SELECT * FROM SystemEvents WHERE ID = {0}"
    cursor.execute(sql.format(id))
    result = cursor.fetchone()

    message.append(LogDetail(id, result[7].strip().lstrip("%%10")))

    cursor.close()
    syslogdb.close()
    return message

class Node(object):
    id = None
    hostname = None
    ip = None
    cpu_usage = None
    mem_usage = None
    status = 0

    def __init__(self, id, hostname, host_ip):
        self.id = id
        self.hostname = hostname
        self.ip = host_ip

    def get_status(self):
        import re
        import subprocess

        regex = re.compile("100% packet loss")
        try:
            p = subprocess.Popen(["ping -c 1 -w 1"+ self.ip],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
            out = p.stdout.read()
            if len(regex.findall(out)) == 0:
                self.status = "Up"
            else:
                self.status = "Down"
        except Exception:
            self.status = "Error"


def node_list(request):
    hypervisors = hypervisor_list(request)
    hypervisors.sort(key=utils.natural_sort('hypervisor_hostname'))

    print hypervisors[0]

    nodelist = []
    for hypervisor in hypervisors:
        node = Node(hypervisor.id, hypervisor.hypervisor_hostname,
                    hypervisor.host_ip)
        node.get_status()
        nodelist.append(node)

    return nodelist

def add_blacklist(request):
    form = request.POST

    print form

    if '' == form['firewall_ip'] or '' == form['ip']:
        return 2

    if '192.168.202.1' != form['firewall_ip']:
        return 1

    cmd = ""

    if '1' == form['time']:
        cmd = 'blacklist ip %s\n' % (form['ip'])
    elif '2' == form['time']:
        cmd = 'blacklist ip %s timeout %s\n' % (form['ip'], '30')
    elif '3' == form['time']:
        cmd = 'blacklist ip %s timeout %s\n' % (form['ip'], '180')
    elif '4' == form['time']:
        cmd = 'blacklist ip %s timeout %s\n' % (form['ip'], '1000')

    cmd = str(cmd)
    finish1 = '<Newtouch-H3C>'
    finish2 = '[Newtouch-H3C]'

    tn = telnetlib.Telnet(form['firewall_ip'])
    tn.read_until('Password:')
    tn.write('newtouch!@#123' + '\n')

    tn.read_until(finish1)
    tn.write('system-view\n')

    tn.read_until(finish2)
    print cmd
    tn.write(cmd)
    tn.write('quit\n')
    tn.write('quit\n')

    tn.close()

    return 0
