from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.newtouch import dashboard

class Server(horizon.Panel):
    name = _("Server")
    slug = "server"


dashboard.Newtouch.register(Server)
