# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

class FilterForm(forms.SelfHandlingForm):
    addr = forms.ChoiceField(
        label=_('Addr'),
        required=True,
        choices=[('ShangHai', _('ShangHai')),
                 ('BeiJing', _('BeiJing')),
                 ('GuangZhou', _('GuangZhou'))])

    start_time = forms.DateTimeField(
        label=_('StartTime'),
        required=False
    )
    end_time = forms.DateTimeField(
        label=_('EndTime'),
        required=False,
    )

    priority = forms.ChoiceField(
        label=_('Priority'),
        required=False,
        choices=[('Any', _('Any')),
                 ('Emergency', _('Emergency')),
                 ('Alert', _('Alert')),
                 ('Critical', _('Critical')),
                 ('Error', _('Error')),
                 ('Warning', _('Warning')),
                 ('Notice', _('Notice')),
                 ('Informational', _('Informational')),
                 ('Debug', _('Debug'))])

    attack_type = forms.ChoiceField(
        label=_('Attack Type'),
        required=False,
        choices=[('Any', _('Any')),
                 ('SHELL', _('SHELL')),
                 ('DPATTACK', _('DPATTACK')),
                 ('FILTER', _('FILTER')),
                 ('DPURPF', _('DPURPF')),
                 ('ARP', _('ARP')),
                 ('WEB', _('WEB')),
                 ('SOCKET', _('SOCKET')),
                 ('CFGMAN', _('CFGMAN')),
                 ('CFM', _('CFM'))]
    )



    srcip = forms.CharField(max_length=15,
                            label=_('SrcIP'),
                            help_text="192.168.7.137",
                            required=False)

    destip = forms.CharField(max_length=15,
                            label=_('DestIP'),
                            help_text="192.168.202.1",
                            required=False)

    def __init__(self, request, *args, **kwargs):
        super(FilterForm, self).__init__(request, *args, **kwargs)

    def clean(self):
        return super(FilterForm, self).clean()

    def handle(self, request, data):
        meta = {'priority': data['priority'],
                'attack_type': data['attack_type'],
                'srcip': (data['srcip']),
                'destip': (data['destip'])}

        try:
            # image = api.glance.image_create(request, **meta)
            filter = []
            # messages.success(request, _('--------------------'))

            return filter
        except Exception:
            exceptions.handle(request, _('Unable to create new image.'))


class AddBlacklistForm(forms.SelfHandlingForm):
    firewall_ip = forms.CharField(max_length=15,
                            label=_('FirewallIP'),
                            initial='192.168.202.1',
                            help_text="192.168.202.1",
                            required=True)

    ip = forms.CharField(max_length=15,
                            label=_('IP'),
                            help_text="192.168.7.137",
                            required=True)

    time = forms.ChoiceField(label=_("Old Time"),
                             choices=[('1', _("EveryTime")),
                                      ('2', _("30 min")),
                                      ('3', _("3 h")),
                                      ('4', _("1000 min")),],
                             initial= '1',
                             widget=forms.RadioSelect(attrs={'default': '1',}))

    def __init__(self, request, *args, **kwargs):
        super(AddBlacklistForm, self).__init__(request, *args, **kwargs)

    def clean(self):
        return super(AddBlacklistForm, self).clean()

    def handle(self, request, data):
        meta = {}

        try:
            blacklist = []
            messages.success(request, _('--------------------'))

            return blacklist
        except Exception:
            exceptions.handle(request, _('Unable to create new blacklist.'))