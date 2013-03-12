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

from requestbuilder import Arg
from .describerequest import DescribeServices
from .adminservice import EucalyptusAdminRequest
from .synckeys import SyncKeys
import os
import sys

class FixPortMetaClass(type):
    """
    I generally avoid metaclasses.  They can be confusing.
    However, I wanted to find a clean way to allow the
    DefaultPort class attribute to be "overridden" and
    have the new value make it's way into Port parameter
    in a seamless way.  This is the best I could come up with.
    """

    def __new__(cls, name, bases, attrs):
        if 'DefaultPort' in attrs:
            for base in bases:
                if hasattr(base, 'ARGS'):
                    for param in getattr(base, 'ARGS'):
                        if hasattr(param, 'dest') and param.dest == 'Port':
                            port = attrs['DefaultPort']
                            setattr(param, 'default', port)
                            param.help = 'Port for service (default=%d)' % port
        return type.__new__(cls, name, bases, attrs)

class RegisterRequest(EucalyptusAdminRequest):

    __metaclass__ = FixPortMetaClass

    ServiceName = ''
    SERVICE_PATH = 'services/Configuration'
    DefaultPort = 8773

    ARGS = [
              Arg('-C', '--component', dest='Name',
                  required=True,
                  help='component name (must be unique)'),
              Arg('-P', '--partititon', dest='Partition',
                  required=True,
                  help='partition the component should join'),
              Arg('-H', '--host', dest='Host',
                  required=True,
                  help="new component's IP address"),
              Arg('-p', '--port', dest='Port',
                  type=int,
                  default=DefaultPort,
                  help="new component's port number (default: %d)" % DefaultPort)
              ]

    def __init__(self, **args):
        self._update_port()
        EucalyptusAdminRequest.__init__(self, **args)

    def _update_port(self):
        # TODO: determine whether this is necessary
        pass

    def main(self):
        EucalyptusAdminRequest.main(self)
        if not self.args.get('no_sync'):
            # TODO: pass a list of keys!
            self._sync_keys(self.KEYS)

    def _sync_keys(self, fnames, host=None):
        key_dir = os.path.join(os.environ.get('EUCALYPTUS', '/'),
                               'var/lib/eucalyptus/keys')
        file_paths = [os.path.join(key_dir, fname % self.args) for fname in fnames]
        req = SyncKeys(file_paths, key_dir, (host or self.args['Host']),
                       use_rsync=(not self.args.get('no_rsync')),
                       use_scp=(not self.args.get('no_scp')))
        return req.sync_keys()

    def print_result(self, data):
        response = data.get('RegisterComponentResponseType', {}) \
                       .get('ConfigurationMessage', {}) \
                       .get('_return')
        if response != 'true':
            # Failed responses still return HTTP 200, so we raise exceptions
            # manually.  See https://eucalyptus.atlassian.net/browse/EUCA-3670.
            msg = data.get('RegisterComponentResponseType', {}) \
                      .get('ConfigurationMessage', {}) \
                      .get('statusMessage', 'registration failed')
            raise RuntimeError('error: ' + msg)
        if len(self.new_partitions) == 1:
            print >> sys.stderr, 'Created new partition \'{0}\''.format(
                    iter(self.new_partitions).next())

        # Mostly copypasted from describeservices.py.  Make sure to refactor
        # this during the rewrite.
        fmt = 'SERVICE\t%-15.15s\t%-15s\t%-15s\t%-10s\t%-4s\t%-40s\t%s'
        if self.service_info:
            service_id = self.service_info['serviceId']
            print fmt % (service_id.get('type'),
                         service_id.get('partition'),
                         service_id.get('name'),
                         self.service_info.get('localState'),
                         self.service_info.get('localEpoch'),
                         service_id.get('uri'),
                         service_id.get('fullName'))
        else:
            print 'Registration ok; no service information is available yet'

    def preprocess(self):
        self.params['Name'] = self.args.get('Name')
        self.params['Partition'] = self.args.get('Partition')
        self.params['Host'] = self.args.get('Host')
        self.params['Port'] = self.args.get('Port')
        self.original_partitions = self.get_partitions()
        
    def print_result(self, data):
        partitions = self.get_partitions() - self.original_partitions
        name = self.args.get('Name')
        service_info = self.get_service_info(name)
        print service_info

    def get_service_info(self, name, debug=0):
        obj = DescribeServices(url=self.args.get('url'))
        response = obj.main()
        statuses = (response.get('serviceStatuses', []))
        for status in statuses:
            svcname = status.get('serviceId', {}).get('name')
            if svcname == name:
                return status

    def get_partitions(self, debug=0):
        obj = DescribeServices(url=self.args.get('url'))
        response = obj.main()
        statuses = (response.get('DescribeServicesResponseType', {})
                            .get('serviceStatuses', []))
        partitions = set()
        for status in statuses:
            partition = status.get('serviceId', {}).get('partition')
            partitions.add(partition)
        return partitions


class RegisterArbitrator(RegisterRequest):
    ServiceName = 'Arbitrator'
    DESCRIPTION = 'Register an Arbitrator service.'

class RegisterCluster(RegisterRequest):
    ServiceName = 'Cluster'
    DESCRIPTION = 'Register a Cluster service.'
    DefaultPort = 8774
    KEYS = ['cloud-cert.pem', 'cloud-pk.pem',
            '%(Partition)s/node-cert.pem',
            '%(Partition)s/node-pk.pem',
            '%(Partition)s/cluster-cert.pem',
            '%(Partition)s/cluster-pk.pem',
            '%(Partition)s/vtunpass']

class RegisterEucalyptus(RegisterRequest):
    ServiceName = 'Cloud'
    DESCRIPTION = 'Register a Cloud service.'
    KEYS = ['euca.p12', 'cloud-cert.pem', 'cloud-pk.pem']

class RegisterStorageController(RegisterRequest):
    ServiceName = 'Storage Controller'
    DESCRIPTION = 'Register a StorageController service.'
    KEYS = ['euca.p12']

    def main(self, **args):
        """
        self.sc_preexists = self.check_for_extant_storage(self.partition,
                                                          debug)
        """

        return RegisterRequest.main(self, **args)

    def check_for_extant_storage(self, partition, debug=False):
        obj = DescribeServices()
        response = obj.main(filter_partition=partition, filter_type='storage',
                            debug=debug)
        statuses = (response.get('euca:DescribeServicesResponseType', {})
                            .get('euca:serviceStatuses', []))
        return len(statuses) > 0

    def print_result(self, data):
        RegisterRequest.print_result(self, data)
        """
        if not self.sc_preexists:
            print >> sys.stderr, \
                    ('Registered the first storage controller in partition '
                     '\'{0}\'.  You must choose a storage back end with '
                     '``euca-modify-property -p {0}.storage.'
                     'blockstoragemanager=$BACKEND\'\'').format(self.partition)
        """


class RegisterWalrus(RegisterRequest):
    ServiceName = 'Walrus'
    DESCRIPTION = 'Register a Walrus service.'
    KEYS = ['euca.p12']
