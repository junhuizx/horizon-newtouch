import netsnmp
from django.template import defaultfilters as filters
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import messages


from openstack_dashboard.dashboards.newtouch.models import ServerMonitorMessage,Server,Service

SNMP_RESTART_HTTPD = '.1.3.6.1.4.1.2021.18'
SNMP_RESTART_NOVA_API = '.1.3.6.1.4.1.2021.19'
SNMP_RESTART_NOVA_COMPUTE = '.1.3.6.1.4.1.2021.20'
SNMP_RESTART_MYSQL = '.1.3.6.1.4.1.2021.21'


def safe_unordered_list(value):
    return filters.unordered_list(value, autoescape=True)

def get_service_list(server):
    services = getattr(server, "services", None)

    return [service.name for service in services.all()]

def server_service_restart(request, **kwargs):
    server = Server.objects.get(pk = kwargs['server_id'])
    service = kwargs['service']

    session = netsnmp.Session(DestHost=server.ip, Version=2, Community=server.snmp_commit)

    if(service.name == 'nova-api'):
        vars = netsnmp.VarList(netsnmp.Varbind(SNMP_RESTART_NOVA_API))
    elif(service.name == 'nova-compute'):
        vars = netsnmp.VarList(netsnmp.Varbind(SNMP_RESTART_NOVA_COMPUTE))
    elif(service.name == 'mysql'):
        vars = netsnmp.VarList(netsnmp.Varbind(SNMP_RESTART_MYSQL))
    elif(service.name == 'apache'):
        vars = netsnmp.VarList(netsnmp.Varbind(SNMP_RESTART_HTTPD))
    else:
        vars = netsnmp.VarList(netsnmp.Varbind(SNMP_RESTART_HTTPD))
    restart_message = session.walk(vars)

    messages.success(request,
                    _('%s') % (restart_message[9]))

def server_service_stop(**kwargs):
    server = Server.objects.get(pk = kwargs['server_id'])
    service = kwargs['service']

def server_service_start(**kwargs):
    server = Server.objects.get(pk = kwargs['server_id'])
    service = kwargs['service']

class FilterAction(tables.FilterAction):
    name = "filter"

class EditActionLink(tables.LinkAction):
    name = "edit_server"
    verbose_name = _("Edit Server")
    url = "horizon:newtouch:server:edit"
    classes = ("ajax-modal",)

class ServicesActionLink(tables.LinkAction):
    name = "edit_service"
    verbose_name = _("Edit Service")
    url = "horizon:newtouch:server:services"
    classes = ("ajax-modal",)

class RestartActionLink(tables.Action):
    name = "restart_service"
    verbose_name = _("Restart Service")
    classes = ("btn-danger",)

    def single(self, table, request, id):
        tag, sep, server_id = request.path.strip("/").partition('/')
        server_id = int(server_id)
        server = Server.objects.get(pk = server_id)

        service = Service.objects.get(pk=id)
        try:
            server_service_restart(request ,server_id=server_id, service=service)
            messages.success(request,
                             _('Successfully Restart %s Service On %s(%s)') % (service.name, server.name, server.ip))
        except Exception:
            exceptions.handle(request,
                              _('Unable to Restart %s Service On %s(%s)') % (service.name, server.name, server.ip))

        return redirect('horizon:newtouch:server:detail', server_id)


class StopActionLink(tables.Action):
    name = "stop_service"
    verbose_name = _("Stop Service")
    classes = ("btn-danger",)

    def single(self, table, request, id):
        tag, sep, server_id = request.path.strip("/").partition('/')
        server_id = int(server_id)
        server = Server.objects.get(pk = server_id)

        service = Service.objects.get(pk=id)
        try:
            server_service_stop(server_id=server_id, service=service)
            messages.success(request,
                             _('Successfully Stop %s Service On %s(%s)') % (service.name, server.name, server.ip))
        except Exception:
            exceptions.handle(request,
                              _('Unable to Stop %s Service On %s(%s)') % (service.name, server.name, server.ip))

        return redirect('horizon:newtouch:server:detail', server_id)

class StartActionLink(tables.Action):
    name = "Start_service"
    verbose_name = _("Start Service")
    classes = ("btn-danger",)

    def single(self, table, request, id):
        tag, sep, server_id = request.path.strip("/").partition('/')
        server_id = int(server_id)
        server = Server.objects.get(pk = server_id)

        service = Service.objects.get(pk=id)
        try:
            server_service_start(server_id=server_id, service=service)
            messages.success(request,
                             _('Successfully Start %s Service On %s(%s)') % (service.name, server.name, server.ip))
        except Exception:
            exceptions.handle(request,
                              _('Unable to Start %s Service On %s(%s)') % (service.name, server.name, server.ip))

        return redirect('horizon:newtouch:server:detail', server_id)

class ServersTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_('Name'),
                         link="horizon:newtouch:server:detail",
                         form_field=forms.CharField(max_length=64))
    ip = tables.Column('ip',
                        verbose_name=_('Description'),
                        form_field=forms.CharField(
                        widget=forms.Textarea(),
                        required=False))
    create_time = tables.Column('create_time', verbose_name=_('Create Time'))
    update_time = tables.Column('update_time', verbose_name=_('Update Time'))
    snmp_version = tables.Column('snmp_version', verbose_name=_('Snmp Version'))
    snmp_commit = tables.Column('snmp_commit', verbose_name=_('Snmp Commit'))
    # ssh_name = tables.Column('ssh_name', verbose_name=_('SSH Name'))
    # ssh_key = tables.Column('ssh_key', verbose_name=_('SSH Key'))
    services = tables.Column(get_service_list,
                             wrap_list=True,
                             filters=(safe_unordered_list,),
                             verbose_name=_('Services'))

    def render(self):
        templates =  super(ServersTable, self).render()
        return templates

    class Meta:
        name = "server"
        verbose_name = _("Server")
        table_actions = (FilterAction,)
        row_actions = (EditActionLink, ServicesActionLink)
        multi_select = False

class ServerMessagesTable(tables.DataTable):
    time = tables.Column('time', verbose_name=_("Time"))
    cpu_usage = tables.Column('cpu_usage', verbose_name=_("CPU Usgae"))
    mem_usage = tables.Column('mem_usage', verbose_name=_("Mem Usage"))
    disk_usage = tables.Column('disk_usage', verbose_name=_("Disk Usage"))
    process_num = tables.Column('process_num', verbose_name=_("Process Num"))

    class Meta:
        name = "server_messages"
        verbose_name = _("Server Messages")
        # row_class = UpdateRow
        # row_actions = (RestartActionLink, StopActionLink, StartActionLink)
        # table_actions = (AddActionLink,)
        multi_select = False


class ServerServicesTable(tables.DataTable):
    server = tables.Column('server', hidden=True, verbose_name=_("Server"))
    name = tables.Column('name', verbose_name=_("Name"))
    status = tables.Column('status', verbose_name=_("Status"))

    class Meta:
        name = "server_services"
        verbose_name = _("Server Services")
        #row_actions = (RestartActionLink, StopActionLink, StartActionLink, )
        row_actions = (RestartActionLink, )
        multi_select = False
