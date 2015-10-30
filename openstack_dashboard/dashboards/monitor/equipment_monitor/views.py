from horizon import tabs,tables

from openstack_dashboard.dashboards.monitor.equipment_monitor import tags as project_tags
from openstack_dashboard.dashboards.monitor.equipment_monitor import tables as project_tables

# from openstack_dashboard import api
from openstack_dashboard.dashboards.monitor import monitor


class IndexView(tabs.TabbedTableView):
    # A very simple class-based view...
    tab_group_class = project_tags.EquipmentMonitorTabs
    template_name = 'monitor/equipment_monitor/index.html'

    # def get_data(self, request, context, *args, **kwargs):
    #     # Add data to the context here...
    #     return context


class InterfaceDetailView(tables.DataTableView):
    table_class = project_tables.InterfaceListTable
    template_name = 'monitor/equipment_monitor/interface_list.html'

    def get_data(self):
        # interfaces = api.monitor.get_interface(self.request, self.kwargs["interface"])
        interfaces = monitor.equipment_monitor_interface_list(self.request, self.kwargs["interface"])
        return interfaces
