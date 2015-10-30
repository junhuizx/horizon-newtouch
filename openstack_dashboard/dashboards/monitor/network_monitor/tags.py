from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from horizon import messages

from openstack_dashboard.dashboards.monitor import monitor
from openstack_dashboard.dashboards.monitor.network_monitor import tables


class AddrBaseTab(tabs.TableTab):
    name = _("")
    slug = ""
    table_classes = (tables.EquipmentListTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_equipment_list_data(self):
        try:
            if self.request.method == "POST":
                # print self.request.POST
                result = monitor.add_blacklist(request = self.request)
                if 0 == result:
                    messages.success(self.request, _("Add Blacklist ok"))
                elif 1 == result:
                    messages.info(self.request, _("Alread in list"))
                else:
                    messages.info(self.request, _("Error"))

            equipments = monitor.network_monitor_equipment_list(request = self.request,
                                                    marker = None,
                                                    paginate = False,
                                                    addr = self.slug)

            return equipments
        except Exception:
            self._has_more = False
            error_message = _('Unable to get instances')
            exceptions.handle(self.request, error_message)

            return []

class ShangHaiTab(AddrBaseTab):
    name = _("ShangHai")
    slug = "shanghai"


class BeijingTab(AddrBaseTab):
    name = _("BeiJing")
    slug = "beijing"


class GuangZhouTab(AddrBaseTab):
    name = _("GuangZhou")
    slug = "guangzhou"


class NetworkMonitorTabs(tabs.TabGroup):
    slug = "network_monitor_tabs"
    tabs = (ShangHaiTab, BeijingTab, GuangZhouTab, )
    sticky = True
