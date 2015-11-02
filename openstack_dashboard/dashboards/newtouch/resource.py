# # -*- coding: utf-8 -*-
import json
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import Resource
from tastypie.exceptions import ApiFieldError, Unauthorized
from tastypie.serializers import Serializer
from openstack_dashboard.dashboards.newtouch import BaseResource
from .models import ServerMonitorMessage,Service,Server
from tastypie.exceptions import BadRequest

class VerboseSerializer(Serializer):
    """
    Gives message when loading JSON fails.
    """
    def from_json(self, content):
        """
        Override method of `Serializer.from_json`. Adds exception message when loading JSON fails.
        """
        try:
            return json.loads(content)
        except ValueError as e:
            raise BadRequest(u"Incorrect JSON format: Reason: \"{}\"".format(e.message))

class ServiceResource(BaseResource):
    class Meta:
        queryset = Service.objects.all()
        resource_name = 'service'
        authorization = Authorization()
        list_allowed_methods = ['post','get',]
        detail_allowed_methods = ['get',]
        always_return_data = True

class ServerResource(BaseResource):
    services = fields.ManyToManyField(ServiceResource,'services')

    class Meta:
        queryset = Server.objects.all()
        resource_name = 'server'
        authorization = Authorization()
        list_allowed_methods = ['post','get', ]
        detail_allowed_methods = ['get',]
        always_return_data = True
    
class ServerMonitorMessageResource(BaseResource):
    server = fields.ForeignKey(ServerResource, 'server')

    class Meta:
        queryset = ServerMonitorMessage.objects.all()
        resource_name = 'server_monitor'
        # authentication = SessionAuthentication()
        # authorization = DjangoAuthorization()
        authorization = Authorization()
        list_allowed_methods = ['post','get', 'patch']
        detail_allowed_methods = ['post','get']
        always_return_data = True
        # serializer = VerboseSerializer(formats=['json'])
