# # -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import ApiFieldError
from tastypie.resources import ModelResource


class BaseResource(ModelResource):
    def apply_filters(self, request, applicable_filters):
        if 'custom' in applicable_filters:
            custom = applicable_filters.pop('custom')
        else:
            custom = None
        semi_filtered = super(BaseResource, self).apply_filters(request, applicable_filters)
        return semi_filtered.filter(custom).distinct() if custom else semi_filtered


    @classmethod
    def full_bundle(cls, obj, request=None, full=True):
        self = cls()
        bundle = self.build_bundle(obj=obj, request=request)
        bundle.full = full
        bundle = self.full_dehydrate(bundle)
        return bundle