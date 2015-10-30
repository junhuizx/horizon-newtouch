from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.dashboards.monitor.equipment_monitor import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^interface/(?P<interface>[^/]+)/$', views.InterfaceDetailView.as_view(), name='interface'),
)
