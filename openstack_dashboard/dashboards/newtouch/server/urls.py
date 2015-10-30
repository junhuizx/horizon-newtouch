from django.conf.urls import patterns
from django.conf.urls import url
from tastypie.api import Api

from openstack_dashboard.dashboards.newtouch import resource
from .views import ServerListView, ServerDetailView, ServerEditView, ServerEditServicesView

api = Api('v1')
api.register(resource.ServerMonitorMessageResource())
api.register(resource.ServerResource())
api.register(resource.ServiceResource())

urlpatterns = patterns(
    '',
    url(r'^$', ServerListView.as_view(), name="index"),
    url(r'^(?P<pk>\d+)/$', ServerDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/edit/$', ServerEditView.as_view(), name='edit'),
    url(r'^(?P<pk>\d+)/add/$', ServerEditServicesView.as_view(), name='services'),
    # url(r'^(?P<pk>\d+)/services/(?P<service_id>\d+)/restart/$', server_service_restart, name='restart'),
    url(r'^(?P<pk>\d+)/services/stop/$', ServerEditServicesView.as_view(), name='stop'),
    url(r'^(?P<pk>\d+)/services/start/$', ServerEditServicesView.as_view(), name='start'),
)
