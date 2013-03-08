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

from .adminservice import EucalyptusAdminRequest
import eucadmin
from requestbuilder import Arg

class DescribeVmTypes(EucalyptusAdminRequest):
    SERVICE_PATH = 'services/Eucalyptus'
    API_VERSION = 'eucalyptus'
    DESCRIPTION = 'Describe the instance types which are available in the system.'
    LIST_MARKERS = ['vmTypeDetails']
    ARGS = [ Arg('-v', '--verbose', dest='Verbose',
                 action='store_true',
                 help='Include extended information about the instance type definition.'),
             Arg('-A', '--availability', dest='Availability',
                 action='store_true',
                 help='Include information about current instance type in the system.'),
             Arg('VmTypes',
                 nargs='?',
                 help='[[INSTANCETYPE]...]')]


    def __init__(self, **args):
      EucalyptusAdminRequest.__init__(self, **args)

    def print_result(self, data):
        import epdb; epdb.st()
        vmtypes = data.get('vmTypeDetails')
        fmt = 'TYPE\t%-20.20s%-10d%-10d%-10d'
        detail_fmt = '%s%06d / %06d %s'
        for vmtype in vmtypes:
            availability = vmtype.get('availability')
            if availability:
              availability_item = availability.get('item')
              print detail_fmt % ((fmt % (vmtype['name'],
                                   int(vmtype['cpu']),
                                   int(vmtype['disk']),
                                   int(vmtype['memory']))),
                                  int(availability_item['available']),
                                  int(availability_item['max']),
                                  availability_item['zoneName'])
            else:
              print fmt % (vmtype['name'],
                           int(vmtype['cpu']),
                           int(vmtype['disk']),
                           int(vmtype['memory']))


