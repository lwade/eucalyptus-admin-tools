# Software License Agreement (BSD License)
#
# Copyright (c) 2009-2013, Eucalyptus Systems, Inc.
# All rights reserved.
#
# Redistribution and use of this software in source and binary forms, with or
# without modification, are permitted provided that the following conditions
# are met:
#
#   Redistributions of source code must retain the above
#   copyright notice, this list of conditions and the
#   following disclaimer.
#
#   Redistributions in binary form must reproduce the above
#   copyright notice, this list of conditions and the
#   following disclaimer in the documentation and/or other
#   materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import argparse
from requestbuilder import Arg, MutuallyExclusiveArgList, AUTH, SERVICE
from requestbuilder.auth import QuerySigV2Auth
from requestbuilder.exceptions import AuthError
from requestbuilder.mixins import TabifyingCommand
import requestbuilder.request
import requestbuilder.service
import requests
import os
import sys
from . import Eucadmin
from eucadmin.getcredentials import GetCredentials

class EucalyptusAdminQuerySigV2Auth(QuerySigV2Auth):
    def configure(self):
        # Environment (for compatibility with EC2 tools)
        if 'EC2_ACCESS_KEY' in os.environ and not self.args.get('key_id'):
            self.args['key_id'] = os.getenv('EC2_ACCESS_KEY')
        if 'EC2_SECRET_KEY' in os.environ and not self.args.get('secret_key'):
            self.args['secret_key'] = os.getenv('EC2_SECRET_KEY')
        # AWS credential file (location given in the environment)
        self.configure_from_aws_credential_file()
        # Regular config file
        # self.configure_from_configfile()

        # That's it; make sure we have everything we need
        if not self.args.get('key_id') and not self.args.get('secret_key'):
            url = None # 'http://localhost:8773/services/Eucalyptus'
            (self.args['key_id'], 
             self.args['secret_key']) = GetCredentials(euca_home=os.environ.get('EUCALYPTUS', '/'),
                                                       account='eucalyptus',
                                                       user='admin').main()

        if not self.args.get('key_id') :
            raise AuthError('missing access key ID; please supply one with -I')
        if not self.args.get('secret_key'):
            raise AuthError('missing secret key; please supply one with -S')


class EucalyptusAdminService(requestbuilder.service.BaseService):
    NAME = 'eucadmin'
    DESCRIPTION = 'Eucalyptus Administrative web service'
    API_VERSION = '2009-11-30'
    AUTH_CLASS  = EucalyptusAdminQuerySigV2Auth
    URL_ENVVAR = 'EC2_URL'

    ARGS = [ MutuallyExclusiveArgList(
                Arg('--region', dest='userregion', metavar='REGION',
                    route_to=SERVICE,
                    help='region name to connect to, with optional identity'),
                Arg('-U', '--url', metavar='URL', route_to=SERVICE,
                    default='http://localhost:8773',
                    help='compute service endpoint URL'))]

    def configure(self):
        # self.args gets highest precedence for self.endpoint and user/region
        self.process_url(self.args.get('url'))
        if self.args.get('userregion'):
            self.process_userregion(self.args['userregion'])
        # Environment
        self.process_url(os.getenv(self.URL_ENVVAR))
        # Regular config file
        self.process_url(self.config.get_region_option(self.NAME + '-url'))

        # Ensure everything is okay and finish up
        self.validate_config()
        if self.auth is not None:
            self.auth.configure()

    def handle_http_error(self, response):
        # TODO: Make an Exception class for this
        raise Exception(response)


class EucalyptusAdminRequest(requestbuilder.request.AWSQueryRequest,
                             TabifyingCommand):
    SUITE = Eucadmin
    SERVICE_CLASS = EucalyptusAdminService
    METHOD = 'POST'

    def __init__(self, **kwargs):
        requestbuilder.request.AWSQueryRequest.__init__(self, **kwargs)
        self.path = getattr(self, 'SERVICE_PATH', None)

    """
    def parse_http_response(self, response_body):
        response = requestbuilder.request.AWSQueryRequest.parse_http_response(
            self, response_body)
        # Compute cloud controller responses enclose their useful data inside
        # FooResponse elements.  If that's all we have after stripping out
        # RequestId then just return its contents.
        useful_keys = filter(lambda x: x != 'RequestId', response.keys())
        if len(useful_keys) == 1:
            return response[useful_keys[0]]
        else:
            return response
    """

    # TODO: Useful output functions
