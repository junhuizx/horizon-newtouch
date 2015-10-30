from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from horizon import messages

from openstack_dashboard.dashboards.monitor import monitor
from openstack_dashboard.dashboards.monitor.equipment_monitor import tables as project_tables
from horizon.utils import functions as utils

class NodeListTab(tabs.TableTab):
    name = _("NodeList")
    slug = "node_list"
    table_classes = (project_tables.NodeListTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_node_list_data(self):
        nodelist = []
        try:
            # nodelist = api.nova.hypervisor_list(self.request)
            # nodelist.sort(key=utils.natural_sort('hypervisor_hostname'))

            nodelist = monitor.node_list(self.request)
            # import  pprint
            # pprint.pprint(type(nodelist[0]))

        except Exception:
            exceptions.handle(self.request,
                _('Unable to retrieve hypervisor information.'))

        return nodelist

class EquipmentListTab(tabs.TableTab):
    name = _("EquipmentList")
    slug = "equipment_list"
    table_classes = (project_tables.EquipmentListTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_equipment_list_data(self):
        try:
            equipments = monitor.equipment_monitor_equipment_list(request = self.request,
                                                    marker = None,
                                                    paginate = False,
                                                    addr = self.slug)

            return equipments
        except Exception:
            self._has_more = False
            error_message = _('Unable to get instances')
            exceptions.handle(self.request, error_message)

            return []

class EquipmentMonitorTabs(tabs.TabGroup):
    slug = "equipment_monitor_tabs"
    tabs = (NodeListTab, EquipmentListTab, )
    sticky = True
