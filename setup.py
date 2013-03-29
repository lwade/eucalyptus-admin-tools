#!/usr/bin/python -tt

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

# from distutils.core import setup
from setuptools import setup
from distutils.command.install_data import install_data

import glob
import os
import sys

class ExecutableDataFiles(install_data):
    def run(self):
        install_data.run(self)
        for x in self.outfiles:
            if x.startswith(sys.prefix+"/lib/eucadmin/validator-scripts/"):
                os.chmod(x, 0755)


setup(name="eucadmin",
      version='0.0.1',
      description="Eucalyptus Admin Tools",
      entry_points = {
          'console_scripts': [
              'euca-configure-vmware = eucadmin.configurevmware:ConfigureVMware.run',
              'euca-deregister-arbitrator = eucadmin.deregisterrequest:DeregisterArbitrator.run',
              'euca-deregister-cloud = eucadmin.deregisterrequest:DeregisterEucalyptus.run',
              'euca-deregister-cluster = eucadmin.deregisterrequest:DeregisterCluster.run',
              'euca-deregister-storage-controller = eucadmin.deregisterrequest:DeregisterStorageController.run',
              'euca-deregister-vmware-broker = eucadmin.configurevmware:DeregisterVMwareBroker.run',
              'euca-deregister-walrus = eucadmin.deregisterrequest:DeregisterWalrus.run',
              'euca-describe-arbitrators = eucadmin.describerequest:DescribeArbitrators.run',
              'euca-describe-clouds = eucadmin.describerequest:DescribeEucalyptus.run',
              'euca-describe-clusters = eucadmin.describerequest:DescribeClusters.run',
              'euca-describe-components = eucadmin.describerequest:DescribeComponents.run',
              'euca-describe-instance-types = eucadmin.instancetypes:DescribeVmTypes.run',
              'euca-describe-nodes = eucadmin.describerequest:DescribeNodes.run',
              'euca-describe-properties = eucadmin.describerequest:DescribeProperties.run',
              'euca-describe-services = eucadmin.describerequest:DescribeServices.run',
              'euca-describe-storage-controllers = eucadmin.describerequest:DescribeStorageControllers.run',
              'euca-describe-vmware-brokers = eucadmin.configurevmware:DescribeVMwareBrokers.run',
              'euca-describe-walruses = eucadmin.describerequest:DescribeWalruses.run',
              'euca-evacuate-node = eucadmin.evacuatenode:EvacuateNode.run',
              'euca-get-credentials = eucadmin.getcredentials:GetCredentials.run',
              'euca-heartbeat = eucadmin.heartbeat:Heartbeat.run',
              'euca-initialize-cloud = eucadmin.initialize:Initialize.run',
              'euca-modify-cluster = eucadmin.modifyclusterattribute:ModifyClusterAttribute.run',
              'euca-modify-instance-type-attribute = eucadmin.instancetypes:ModifyVmTypeAttribute.run',
              'euca-modify-property = eucadmin.modifypropertyvalue:ModifyPropertyValue.run',
              'euca-modify-service = eucadmin.modifyservice:ModifyService.run',
              'euca-modify-storage-controller = eucadmin.modifystoragecontroller:ModifyStorageControllerAttribute.run',
              'euca-modify-walrus = eucadmin.modifywalrus:ModifyWalrusAttribute.run',
              'euca-register-arbitrator = eucadmin.registerrequest:RegisterArbitrator.run',
              'euca-register-cloud = eucadmin.registerrequest:RegisterEucalyptus.run',
              'euca-register-cluster = eucadmin.registerrequest:RegisterCluster.run',
              'euca-register-storage-controller = eucadmin.registerrequest:RegisterStorageController.run',
              'euca-register-vmware-broker = eucadmin.configurevmwar:RegisterVMwareBroker.run',
              'euca-register-walrus = eucadmin.registerrequest:RegisterWalrus.run',
              'euca-setup = eucadmin.eucasetup:EucaSetup.run',
              'euca-validator = eucadmin.validator:Validator.run',
          ],
      },
      long_description="CLI for Eucalyptus administration",
      author="Andy Grimm",
      author_email="agrimm@gmail.com",
      url="http://eucalyptus.com/",
      packages=['eucadmin'],
      license='BSD',
      platforms='Posix; MacOS X; Windows',
      classifiers=[ 'Development Status :: 3 - Alpha',
                      'Intended Audience :: Developers',
                      'License :: OSI Approved :: BSD License',
                      'Operating System :: OS Independent',
                      'Topic :: Internet',
                      ],
      install_requires=[
          "requestbuilder",
          "argparse",
          "PyYAML",
      ],
      scripts=[
          "bin/euca_conf",
      ],
      data_files=[
          (sys.prefix+"/lib/eucadmin", ['config/validator.yaml']),
          (sys.prefix+"/lib/eucadmin/validator-scripts", glob.glob('validator-scripts/*')),
      ],
      cmdclass={'install_data':  ExecutableDataFiles},

)
