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

from .command import Command
from .cmdstrings import get_cmdstring
import eucadmin
import os
import sys
import time
import pgdb as db
import hashlib
import binascii
from M2Crypto import RSA
from requestbuilder import Arg
from requestbuilder.command import BaseCommand

EucaP12File = '%s/var/lib/eucalyptus/keys/euca.p12'
CloudPKFile = '%s/var/lib/eucalyptus/keys/cloud-pk.pem'

class GetCredentials(BaseCommand):
    # ServiceClass = eucadmin.EucAdmin
    DESCRIPTION = ("Download a user's credentials to <zipfile>.  New X.509 "
                   "credentials are created each time this command is called.")

    # TODO: check if self.ServiceClass.InstallPath is the Euca home
    ARGS = [Arg('--euca_home', dest='euca_home',
                default=os.environ.get('EUCALYPTUS', '/'),
                help='Eucalyptus install dir, default is $EUCALYPTUS'),
            Arg('-a', '--account', dest='account',
                default='eucalyptus',
                help=('account containing the user for which to get '
                      'credentials (default: eucalyptus)')),
            Arg('-u', '--user', dest='user',
                default='admin',
                help=('user name for which to get credentials '
                      '(default: admin)'))]

    def check_cloudpk_file(self):
        if os.path.exists(self.cloudpk_file):
            stats = os.stat(self.cloudpk_file)
            if stats.st_size > 0:
                return True
        return False

    def gen_cloudpk_file(self):
        cmd_string = get_cmdstring('openssl')
        cmd = Command(cmd_string % (self.eucap12_file, self.cloudpk_file))

    def get_dbpass(self):
        def passphrase_callback():
            return "eucalyptus"
        d = hashlib.sha256()
        d.update("eucalyptus")
        pk = RSA.load_key(self.cloudpk_file,passphrase_callback)
        self.db_pass = binascii.hexlify(pk.sign(d.digest(),algo="sha256"))

    def print_result(self, data):
        print ' '.join(data)

    def setup_query(self):
        self.db_pass = None
        
        self.eucap12_file = EucaP12File % self.args.get('euca_home')
        self.cloudpk_file = CloudPKFile % self.args.get('euca_home')
        if not self.check_cloudpk_file():
            self.gen_cloudpk_file()
        self.get_dbpass()

    def main(self):
        self.setup_query()
        con1 = db.connect(host='localhost:8777', user='eucalyptus', password=self.db_pass, database='eucalyptus_auth')
        cur1 = con1.cursor()
        cur1.execute("""select k.auth_access_key_query_id, k.auth_access_key_key 
                          from auth_access_key k 
                          join auth_user u on k.auth_access_key_owning_user=u.id
                          join auth_group_has_users gu on u.id=gu.auth_user_id 
                          join auth_group g on gu.auth_group_id=g.id 
                          join auth_account a on g.auth_group_owning_account=a.id 
                         where a.auth_account_name=%(acctname)s and g.auth_group_name=%(grpname)s and k.auth_access_key_active=TRUE""",
                     params={'acctname': self.args.get('account'), 
                             'grpname': '_' + self.args.get('user')})
        result = cur1.fetchall()
        if not len(result):
            return []
        return result[0]

