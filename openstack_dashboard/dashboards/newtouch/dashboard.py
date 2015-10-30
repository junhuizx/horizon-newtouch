from django.utils.translation import ugettext_lazy as _

import horizon


class ServerPanels(horizon.PanelGroup):
    slug = "server"
    name = _("Server")
    panels = ('overview',
              'server',)

class AlertPanels(horizon.PanelGroup):
    slug = "alert"
    name = _("Alert")
    panels = ('rules',
              'event',)

class Newtouch(horizon.Dashboard):
    name = _("Newtouch")
    slug = "newtouch"
    panels = (ServerPanels, AlertPanels)  # Add your panels here.
    default_panel = 'server'  # Specify the slug of the dashboard's default panel.


horizon.register(Newtouch)
