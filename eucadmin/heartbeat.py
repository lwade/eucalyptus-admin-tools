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

import urlparse

from adminservice import EucalyptusAdminRequest
from requestbuilder import Arg
from requestbuilder.auth import BaseAuth
import argparse

class Heartbeat(EucalyptusAdminRequest):
    SERVICE_PATH = 'services/Heartbeat'
    DESCRIPTION = "Get high-level status information about a system"
    METHOD = 'GET'

    ARGS = [ Arg('Host', 
                 help='Get heartbeat data for <host>.'),
             Arg('-p', '--port',
                 default='8773',
                 help='The web service port (Default: 8773)') ]
    
    def configure(self):
        scheme = 'http'
        self.service.auth = BaseAuth(self.service)
        self.args.get('Host')
        t = (scheme, '%s:%s' % (self.args.get('Host'), 
                                self.args.get('port')), 
                                '', '', '')
        self.service.endpoint = urlparse.urlunsplit(t)
         
        EucalyptusAdminRequest.configure(self)

    @property
    def default_route(self):
        return None

    def prepare_params(self):
        pass

    def __repr__(self):
        return '<Heartbeat: %s>' % self.url

    def _get_value(self, value):
        if value == 'true':
            value = True
        elif value == 'false':
            value = False
        return value

    def parse_response(self, resp):
        lines = resp.content.splitlines()
        data = {}
        for line in lines:
            pairs = line.split()
            t = pairs[0].split('=')
            d = {}
            data[t[1]] = d
            for pair in pairs[1:]:
                t = pair.split('=')
                d[t[0]] = self._get_value(t[1])
        return data

    def print_result(self, data):
        for key in data:
            val = data[key]
            print '%s:\tlocal=%s\tinitialize=%s\tenabled=%s' % (key, val['local'],
                                                                val['initialized'],
                                                                val['enabled'])

