import datetime
import random
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response, render
# from django.views.generic import ListView,DetailView
import time
from openstack_dashboard.dashboards.newtouch.models import ServerMonitorMessage,Server,Service
from openstack_dashboard.dashboards.newtouch.server import tables as project_tables
from openstack_dashboard.dashboards.newtouch.server import forms as project_forms

from horizon import tables,forms


# Create your views here.
class ServerEditView(forms.ModalFormView):
    template_name = 'newtouch/server/edit.html'
    form_class = project_forms.EditServerForm
    success_url = reverse_lazy('horizon:newtouch:server:index')

    def get_initial(self):
        server = Server.objects.get(pk=self.kwargs["pk"])
        return {'pk': self.kwargs["pk"],
                'snmp_commit': server.snmp_commit,
                'snmp_version':server.snmp_version,
                'ssh_name': server.ssh_name,
                'ssh_key': server.ssh_key}

    def get_context_data(self, **kwargs):
        context = super(ServerEditView, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        return context

class ServerEditServicesView(forms.ModalFormView):
    template_name = 'newtouch/server/edit_services.html'
    form_class = project_forms.ServerEditServicesForm
    success_url = reverse_lazy('horizon:newtouch:server:index')

    def get_initial(self):
        server = Server.objects.get(pk=self.kwargs["pk"])
        return {'pk': self.kwargs["pk"],
                'services_available':[service.name for service in server.services.all()]}

    def get_context_data(self, **kwargs):
        context = super(ServerEditServicesView, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        server = Server.objects.get(pk=self.kwargs["pk"])
        context['service_used'] = [service.name for service in server.services.all()]
        return context

class ServerDetailService(object):
    id = None
    name = None
    status = None

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.name = kwargs['name']
        self.status = kwargs['status']
        self.server = kwargs['server']

    def __str__(self):
        return self.name

class ServerDetailChart(object):
    def __init__(self, **kwargs):
        self.type = kwargs['type']
        self.data = kwargs['data']
        self.container = kwargs['container']
        self.extra = kwargs['extra']

    def __str__(self):
        return self.type

class ServerListView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'newtouch/server/index.html'
    table_class = project_tables.ServersTable

    def get_data(self):
        # Add data to the context here...
        server_list = Server.objects.all()

        return server_list

class ServerDetailView(tables.MultiTableView):
    table_classes = (project_tables.ServerServicesTable, project_tables.ServerMessagesTable)
    template_name = 'newtouch/server/server_detail.html'
    failure_url = reverse_lazy('horizon:newtouch:server:index')

    def get_server_services_data(self, **kwargs):
        server_id = self.kwargs.get('pk')
        services = []

        last_server_message = ServerMonitorMessage.objects.all().filter(server=Server.objects.get(pk=server_id)).order_by("-id")[0]
        service_status = last_server_message.process_status.lstrip("{").rstrip("}").split(',')

        for service in service_status:
            service = str(service)
            name, sep, status = service.partition(":")
            name = name.strip().lstrip("u").strip("'")
            id = Service.objects.get(name=name).id
	    status = status.strip()
            if(status == '1'):
                status = 'UP'
            else:
                status = 'DOWN'
            services.append(ServerDetailService(id = id,server = server_id,name= name, status=status))

        return services

    def get_server_messages_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        server_messages = ServerMonitorMessage.objects.all().filter(server=Server.objects.get(pk=pk)).order_by("-id")

        if len(server_messages) > 20:
            server_messages = list(server_messages)[:20]

        return server_messages

    # def get_queryset(self, **kwargs):
    #     pk = self.kwargs.get('pk')
    #     server_detail_list = super(ServerDetailView, self).get_queryset()
    #     server_detail_list = server_detail_list.filter(server=Server.objects.get(pk=pk))
    #
    #     return server_detail_list
    #
    def get_context_data(self, **kwargs):
        context = super(ServerDetailView, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk')

        monitor_message_list = ServerMonitorMessage.objects.all().filter(server=Server.objects.get(pk=pk))
	monitor_message_list = list(monitor_message_list)[-24:]

        tooltip_date = "%d %b %Y %H:%M:%S %p"
        extra_serie = {
            "tooltip": {"y_start": "There are ", "y_end": " calls"},
            "date_format": tooltip_date,
            # 'color': '#a4c639'
        }
        xdata = [int(time.mktime(message.time.timetuple()) * 1000) for message in monitor_message_list]
        ydata = [str(message.cpu_usage) for message in monitor_message_list]
        ydata2 = [str(message.mem_usage) for message in monitor_message_list]
        ydata3 = [str(message.disk_usage) for message in monitor_message_list]

        data = {
            'x': xdata,
            'name1': 'cpu', 'y1': ydata, 'extra1': extra_serie,
            'name2': 'memory', 'y2': ydata2, 'extra2': extra_serie,
            'name3': 'disk', 'y3': ydata3, 'extra3': extra_serie,
        }

        extra = {
            'x_is_date': True,
            'x_axis_format': '%b %d %H:%M:%S',
            'tag_script_js': True,
            'jquery_on_ready': False,
        }

        chart1 = ServerDetailChart(type="lineChart",
                                   container="linechart_container",
                                   data=data,
                                   extra=extra)
        context["chart1"] = chart1

        return context
