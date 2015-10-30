# The name of the dashboard to be added to HORIZON['dashboards']. Required.
DASHBOARD = 'newtouch'

# If set to True, this dashboard will not be added to the settings.
DISABLED = False

# A dictionary of exception classes to be added to HORIZON['exceptions'].
ADD_EXCEPTIONS = {}

# A list of applications to be added to INSTALLED_APPS.
ADD_INSTALLED_APPS = [
    'openstack_dashboard.dashboards.newtouch',
]
