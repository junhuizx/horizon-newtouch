from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.monitor import dashboard


class Network_Monitor(horizon.Panel):
    name = _("Network_Monitor")
    slug = "network_monitor"


dashboard.Monitor.register(Network_Monitor)
