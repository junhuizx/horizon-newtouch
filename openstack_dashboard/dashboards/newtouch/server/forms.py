from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard.dashboards.newtouch.models import Server,Service

def get_available_services():
    services = Service.objects.all()

    return ((service.name, service.name) for service in services)


class ServerEditServicesForm(forms.SelfHandlingForm):
    services_available = forms.MultipleChoiceField(label=_('services_available'),
                                                    widget=forms.CheckboxSelectMultiple,
                                                    choices=get_available_services())


    def __init__(self, request, *args, **kwargs):
        super(ServerEditServicesForm, self).__init__(request, *args, **kwargs)

    def handle(self, request, data):
        try:
            server = Server.objects.get(pk=self.initial['pk'])
            server.services.clear()

            print server.services.all()
            for service in data['services_available']:
                server.services.add(Service.objects.get(name=service).id)

            server.save()
            message = _('Successfully Add Services %s') % (self.initial['pk'])
            messages.success(request, message)
        except Exception:
            exceptions.handle(request, _('Unable to Add Services.'))
        return True


class EditServerForm(forms.SelfHandlingForm):
    snmp_version = forms.CharField(label=_("SNMP Version"),
                                   max_length=255)
    snmp_commit = forms.CharField(label=_("SNMP Commit"),
                                  max_length=255)
    ssh_name = forms.CharField(label=_("SSH Name"),
                               max_length=255,
                               required=False)
    ssh_key = forms.CharField(label=_("SSH Key"),
                              max_length=255,
                              required=False)

    def __init__(self, request, *args, **kwargs):
        super(EditServerForm, self).__init__(request, *args, **kwargs)

    def handle(self, request, data):
        pk = self.initial['pk']
        snmp_version = data['snmp_version']
        snmp_commit = data['snmp_commit']
        ssh_name = data['ssh_name']
        ssh_key = data['ssh_key']

        try:
            Server.objects.filter(pk=pk).update(snmp_version=snmp_version,
                                                snmp_commit=snmp_commit,
                                                ssh_name=ssh_name,
                                                ssh_key=ssh_key)
            server_name = Server.objects.get(pk = pk).name
            message = _('Successfully update Server %s') % (server_name)
            messages.success(request, message)
        except Exception:
            exceptions.handle(request, _('Unable to update the Server.'))
        return True
