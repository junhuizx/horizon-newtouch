from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.dashboards.monitor.network_monitor import views


urlpatterns = patterns('openstack_dashboard.dashboards.monitor.network_monitor.views',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^equipment/(?P<equipment_id>[^/]+)/$', views.EquipmentDetailView.as_view(), name='equipment'),
    url(r'^interface/(?P<interface>[^/]+)/$', views.InterfaceDetailView.as_view(), name='interface'),
    url(r'^detail/(?P<message_id>[^/]+)/$', views.MessageDetailView.as_view(), name='detail'),
    url(r'^filter/$', views.NetworkMonitorFilterView.as_view(), name='filter'),
    url(r'^filteraction/$', views.NetworkMonitorFilterActionView.as_view(), name='filteraction'),
    url(r'^blacklist/(?P<equipment_id>[^/]+)/$', views.BlackListView.as_view(), name='blacklist'),
    # url(r'^addblacklist/$', views.BlackListActionView.as_view(), name='addblacklist'),
    # url(r'^addblacklist/(?P<equipment_id>[^/]+)/$', views.BlackListView.as_view(), name='addblacklist'),
)
