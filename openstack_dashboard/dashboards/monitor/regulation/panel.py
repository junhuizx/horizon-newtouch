from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.monitor import dashboard


class Regulation(horizon.Panel):
    name = _("Regulation")
    slug = "regulation"


dashboard.Monitor.register(Regulation)
