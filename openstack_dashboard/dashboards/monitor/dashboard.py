from django.utils.translation import ugettext_lazy as _

import horizon


class Monitor(horizon.Dashboard):
    name = _("Monitor")
    slug = "monitor"
    panels = ('overview', 'regulation', 'network_monitor', 'equipment_monitor')  # Add your panels here.
    default_panel = 'overview'  # Specify the slug of the dashboard's default panel.


horizon.register(Monitor)
