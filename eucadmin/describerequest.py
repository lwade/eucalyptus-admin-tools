# Copyright 2011-2012 Eucalyptus Systems, Inc.
#
# Redistribution and use of this software in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from requestbuilder.request import BaseRequest
from requestbuilder import Arg
import eucadmin
import math
from eucadmin import utils
from .adminservice import EucalyptusAdminRequest
import os

class DescribeRequest(EucalyptusAdminRequest):
    API_VERSION = '2013-02-14'
    LIST_TAGS = ['registered']
    ITEM_MARKERS = ['item']

    def __init__(self, **args):
        EucalyptusAdminRequest.__init__(self, **args)
        self.path = 'services/Configuration'

    def print_result(self, result):
        services = result.get('DescribeComponentsResponseType', {}) \
                         .get('registered')
        fields = {'partition' : 15,
                  'name' : 15,
                  'hostName' : 25}
        for s in services:
            if s.get('hostName', None) != 'detail':
                for field_name in fields:
                    if len(s.get(field_name)) > fields[field_name]:
                        fields[field_name] = len(s.get(field_name))
        fmt = '%%s\t%%-%s.%ss\t%%-%d.%ds\t%%-%ds\t%%s\t%%s' % (fields['partition'],
                                                               fields['partition'],
                                                               fields['name'],
                                                               fields['name'],
                                                               fields['hostName'])
        for s in services:
            if s.get('hostName', None) != 'detail':
                print fmt % (
                    self.ServiceName.upper(),
                    s.get('partition', None),
                    s.get('name', None),
                    s.get('hostName', None),
                    s.get('state', None),
                    s.get('detail', None))


class DescribeArbitrators(DescribeRequest):
    ServiceName = 'Arbitrator'
    DESCRIPTION = 'List Arbitrator services.'

class DescribeClusters(DescribeRequest):
    ServiceName = 'Cluster'
    DESCRIPTION = 'List Cluster services.'

class DescribeStorageControllers(DescribeRequest):
    ServiceName = 'StorageController'
    DESCRIPTION = 'List StorageController services.'

class DescribeWalruses(DescribeRequest):
    ServiceName = 'Walrus'
    DESCRIPTION = 'List Walrus services.'

class DescribeNodes(DescribeRequest):
    ServiceName = 'Node'
    DESCRIPTION = 'List Node controllers.'
    LIST_TAGS = ['registered', 'instances']

    def __init__(self, **kwargs):
        DescribeRequest.__init__(self, **kwargs)

    def print_result(self, data):
        nodes = data.get('registered')
        for node in nodes:
            instances = node.get('instances')
            if isinstance(instances, list):
                instance_ids = [instance.get('entry') for instance in
                                node.get('instances', [])]
            else:
                # If boto's XML parsing bug hasn't been fixed then instances
                # will be a dict with only one or zero instances per node.
                instance_ids = []
            fmt = ['NODE', node.get('name'), node.get('clusterName')]
            fmt.extend(instance_ids)
            print '\t'.join(map(str, fmt))

class DescribeEucalyptus(DescribeRequest):
    ServiceName = 'Cloud'
    DESCRIPTION = 'List Cloud services.'

    def print_result(self, data):
        clouds = data.get('registered')
        for cloud in clouds:
            print self.tabify('CLOUDS',
                              cloud['partition'],
                              cloud['name'],
                              cloud['hostName'],
                              cloud['state'],
                              cloud['detail'])

class DescribeComponents(DescribeRequest):
    ServiceName = 'Component'
    DESCRIPTION = 'List Components.'

    def print_result(self, data):
        components = data.get('registered')
        fmt = 'COMPONENT\t%-15.15s\t%-15.15s\t%-25s\t%s\t%s\t%s'
        for c in components:
            if c.get('hostName', None) != 'detail':
                print fmt % (c.get('partition', None),
                             c.get('name', None),
                             c.get('hostName', None),
                             c.get('fullName', None),
                             c.get('state', None),
                             c.get('detail', None))

class DescribeProperties(DescribeRequest):
    ServiceName = 'Property'
    DESCRIPTION = 'List properties.'
    LIST_TAGS = ['properties']

    def print_result(self, data):
        props = data.get('properties')
        for prop in props:
            print self.tabify([ 'PROPERTY', prop['name'], prop['value'] ])

class DescribeServices(EucalyptusAdminRequest):

    DESCRIPTION = 'Get services'
    LIST_TAGS = ['serviceStatuses']
    METHOD = 'GET'
    SERVICE_PATH = 'services/Empyrean/'

    ARGS = [
              Arg('-A', '--all', dest='ListAll',
                  action="store_true", default=False,
                  help='Include all public service information.  Reported state information is determined by the view available to the target host, which should be treated as advisory (See documentation for guidance on interpreting this information).'),
              Arg('--system-internal', dest='ListInternal',
                  action="store_true", default=False,
                  help='Include internal services information (note: this information is only for the target host).'),
              Arg('--user-services', dest='ListUserServices',
                  action="store_true", default=False,
                  help='Include services which are user facing and are co-located with some other top-level service (note: this information is only for the target host).'),
              Arg('-E', '--events', dest='ShowEvents',
                    action="store_true", default=False,
                    help='Show service event details.'),
              Arg('--events-verbose', dest='ShowEventStacks',
                    action="store_true", default=False,
                    help='Show verbose service event details.')
              ]

    def preprocess(self):
        self.params['ListAll'] = repr(self.args.get('ListAll', False))
        self.params['ListInternal'] = repr(self.args.get('ListInternal', False))
        self.params['ShowEvents'] = repr(self.args.get('ShowEvents', False))
        self.params['ShowEventStacks'] = repr(self.args.get('ShowEventStacks', False))

    def print_result(self, data):
        services = data.get('serviceStatuses')
        fmt = 'SERVICE\t%-15.15s\t%-15s\t%-15s\t%-10s\t%-4s\t%-40s\t%s'
        detail_fmt = 'SERVICEEVENT\t%-36.36s\t%s'
        for s in services:
            service_id = s['serviceId']
            print fmt % (service_id.get('type'),
                         service_id.get('partition'),
                         service_id.get('name'),
                         s.get('localState'),
                         s.get('localEpoch'),
                         service_id.get('uri'),
                         service_id.get('fullName'))
            details = s.get('statusDetails')
            if details:
                detail_item = details.get('item')
                if detail_item:
                    print detail_fmt % (detail_item.get('uuid'),
                                        detail_item.get('serviceFullName'))
                    print detail_fmt % (detail_item.get('uuid'),
                                        detail_item.get('euca:severity'))
                    print detail_fmt % (detail_item.get('uuid'),
                                        detail_item.get('timestamp'))
                    print detail_fmt % (detail_item.get('uuid'),
                                        detail_item.get('message'))
                    if detail_item.get('stackTrace'):
                        print detail_item['stackTrace']
                    print

