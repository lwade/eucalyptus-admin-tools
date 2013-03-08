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

import eucadmin
from requestbuilder import Arg
from .adminservice import EucalyptusAdminRequest

class DeregisterRequest(EucalyptusAdminRequest):
    ServiceName = ''
    SERVICE_PATH = 'services/Configuration'

    @property
    def DESCRIPTION(self):
        return 'De-register a ' + self.ServiceName

    ARGS = [Arg('-P', '--partition', dest='Partition',
                help='partition in which the component participates'),
            Arg('--name', dest='Name',
                required=True,
                help='component name')]

    def preprocess(self):
        self.params['Name'] = self.args.get('Name')
        self.params['Partition'] = self.args.get('Partition')

    def print_result(self, data):
        response = data.get('DeregisterComponentResponseType', {}) \
                       .get('ConfigurationMessage', {}) \
                       .get('_return')
        if response != 'true':
            # Failed responses still return HTTP 200, so we raise exceptions
            # manually.  See https://eucalyptus.atlassian.net/browse/EUCA-3670.
            msg = data.get('statusMessage', 'de-registration failed')
            raise RuntimeError('error: ' + msg)


class DeregisterArbitrator(DeregisterRequest):
    ServiceName = 'Arbitrator'

class DeregisterCluster(DeregisterRequest):
    ServiceName = 'Cluster'

class DeregisterEucalyptus(DeregisterRequest):
    ServiceName = 'Cloud'

class DeregisterStorageController(DeregisterRequest):
    ServiceName = 'StorageController'

class DeregisterWalrus(DeregisterRequest):
    ServiceName = 'Walrus'
