from django.utils.translation import ugettext_lazy as _

from horizon import tables

class EquipmentListFilterAction(tables.FilterAction):
    name = "filter"

class NodeListTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"), hidden=True)
    hostname = tables.Column("hostname",
                         verbose_name=_("Hostname"),
                         link="#")
    ip = tables.Column('ip', verbose_name=_("Ip"))
    # temperature = tables.Column("temperature", verbose_name=_("Temperature"))
    # cpu_usage = tables.Column('cpu_usage', verbose_name=_("CpuUsage"))
    # mem_usage = tables.Column('mem_usage', verbose_name=_("MemUsage"))
    status = tables.Column('status', verbose_name=_("Status"))

    def get_object_id(self, datum):
        return "%s" % (datum.id)

    class Meta:
        name = "node_list"
        verbose_name = _("NodeList")
        table_actions = (EquipmentListFilterAction, )
        multi_select = False

class EquipmentListTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"), hidden=True)
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="#")
    ip = tables.Column('ip', verbose_name=_("Ip"))
    temperature = tables.Column("temperature", verbose_name=_("Temperature"))
    cpu_usage = tables.Column('cpu_usage', verbose_name=_("CpuUsage"))
    mem_usage = tables.Column('mem_usage', verbose_name=_("MemUsage"))
    max_connect_num = tables.Column('max_connect_num', verbose_name=_("MaxConnectNum"))
    cur_connect_num = tables.Column('cur_connect_num', verbose_name=_("CurConnectNum"))
    interface_num = tables.Column('interface_num',
                                  verbose_name=_("InterFaceNum"),
                                  link="horizon:monitor:equipment_monitor:interface")

    def get_object_id(self, datum):
        return "%s-%s" % (datum.id, datum.interface_num)

    class Meta:
        name = "equipment_list"
        verbose_name = _("Equipment List")
        table_actions = (EquipmentListFilterAction, )
        multi_select = False


class InterfaceListTable(tables.DataTable):
    id = tables.Column("id", hidden=True)
    name = tables.Column("name", verbose_name=_("Name"))
    ip = tables.Column("ip", verbose_name=_("IP"))
    inoctets = tables.Column("inoctets", verbose_name=_("InOctets"))
    outoctets = tables.Column("outoctets", verbose_name=_("OutOctets"))
    indiscards = tables.Column("indiscards", verbose_name=_("InDiscards"))
    outdiscards = tables.Column("outdiscards", verbose_name=_("OutDiscards"))
    inerrors = tables.Column("inerrors", verbose_name=_("InErrors"))
    outerrors = tables.Column("outerrors", verbose_name=_("OutErrors"))
    status = tables.Column("status", verbose_name=_("Status"))

    class Meta:
        name = 'interface list'
        verbose_name = _("Interface List")
        multi_select = False
