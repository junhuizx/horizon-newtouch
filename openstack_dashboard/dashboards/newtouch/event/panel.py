from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.newtouch import dashboard


class Event(horizon.Panel):
    name = _("Event")
    slug = "event"


dashboard.Newtouch.register(Event)
