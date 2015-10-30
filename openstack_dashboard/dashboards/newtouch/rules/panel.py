from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.newtouch import dashboard


class Rules(horizon.Panel):
    name = _("Rules")
    slug = "rules"


dashboard.Newtouch.register(Rules)
