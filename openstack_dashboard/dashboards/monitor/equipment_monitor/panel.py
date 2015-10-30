from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.monitor import dashboard


class Equipment_Monitor(horizon.Panel):
    name = _("Equipment_Monitor")
    slug = "equipment_monitor"


dashboard.Monitor.register(Equipment_Monitor)
