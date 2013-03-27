#!/usr/bin/python

import yaml
import os
import argparse
import json
import subprocess
import sys
import paramiko
import urllib
import urlparse
import logging

from .configfile import ConfigFile
from .describerequest import DescribeServices
from .describerequest import DescribeNodes
from .sshconnection import SshConnection
from .constants import *
import debug

sys.excepthook = debug.gen_except_hook(True, True)

check_path = [ os.path.join(cfg_dir, "check.d"),
               os.path.join(cfg_dir, "mmcheck.d"),
               os.path.join(data_dir, "check.d"),
               os.path.join(data_dir, "mmcheck.d"),
               os.path.join(os.path.dirname(__file__), '..', 'check.d'),
               os.path.join(os.path.dirname(__file__), '..', 'mmcheck.d'),
             ]

# Currently, these three are the only components returned by
# DescribeServices that we traverse.
component_map = { 'cluster': 'CC',
                  'storage': 'SC',
                  'walrus':  'WS',
                }

def read_validator_config(files=[]):
    '''
    Read one or more YAML config files and merge them.
    '''

    def merge(base, overlay):
        if isinstance(base, dict) and isinstance(overlay, dict):
            for k,v in overlay.iteritems():
                if k not in base:
                    base[k] = v
                else:
                    base[k] = merge(base[k],v)
        elif isinstance(base, list) and isinstance(overlay, list):
            # We could use sets here, but this preserves
            # ordering, simply eliminating duplicates
            base.extend([ x for x in overlay if x not in base ])
        return base

    data = {}
    for f in files:
        if os.path.exists(f):
            data = merge(data, yaml.load(open(f, 'r').read()))
    return data


def build_parser():
    parser = argparse.ArgumentParser(prog='Eucalyptus cloud validator')
    parser.add_argument('-d', '--euca-home', dest='eucalyptus',
                        default=os.environ.get('EUCALYPTUS', '/'))
    parser.add_argument('stage',
                        default='monitor')
    parser.add_argument('-c', '--config-file',
                        default=None)
    parser.add_argument('-C', '--component',
                        default='CLC',
                        help='The cloud component role(s) of this system.')
    parser.add_argument('-t', '--traverse', 
                        action='store_true',
                        help='Traverse other components in the cloud (requires ssh credentials)')
    parser.add_argument('-j', '--json',
                        action='store_true',
                        help='Output JSON-formatted results')
    parser.add_argument('-q', '--quiet',
                        action='store_true',
                        help='No output; only a return code')
    return parser

def run_script(scriptPath):
    po = subprocess.Popen([scriptPath], 
                          stdout=subprocess.PIPE,
                          cwd='/')
    stdout = po.communicate()[0]
    return stdout

def run_remote(host, component, stage, traverse=False):
   t=traverse and "-t" or ""
   ssh = SshConnection(host, username="root")
   cmd = 'euca-validator %s -C %s %s -j' % (t, component_map.get(component, component), stage)
   out = ssh.cmd(cmd, timeout=600)
   try:
       out['output'] = json.loads(out['output'])
       return out
   except Exception, e:
       return {'cmd': cmd, "output": { "euca-validator": { "failed": 1, "error": str(e) } } }

class Validator(object):
    def __init__(self, stage="monitor", component="CLC", traverse=False, **kwargs):
        if stage != 'preinstall' or (component == "CC" and traverse):
            self.euca_conf = ConfigFile(os.path.join(kwargs.get('eucalyptus', '/'),
                                        'etc/eucalyptus/eucalyptus.conf'))

        # TODO: allow a component list?
        os.environ['EUCA_ROLES'] = component
        self.stage = stage
        self.component = component
        self.traverse = traverse

        self.setupLogging()

    def setupLogging(self):
        self.log = logging.getLogger(__name__)

    @classmethod
    def run(cls):
        parser = build_parser()
        args = parser.parse_args()
        obj = cls(**vars(args))
        result = obj.main()
        if args.json:
            print json.dumps(result, indent=4)
        elif args.quiet:
            sys.exit(Validator.check_nested_result("", result))
        else:
            sys.exit(Validator.check_nested_result("", result, print_output=True))

    @staticmethod
    def check_nested_result(parent, result, print_output=False):
        failed = False
        for key in result.keys():
            if type(result[key]) != dict:
                import epdb; epdb.st()
            if result[key].has_key('cmd'):
                failed |= Validator.check_nested_result(parent + key + ":", 
                                                        result[key]['output'],
                                                        print_output=print_output)
            elif not result[key].has_key('failed'):
                failed |= Validator.check_nested_result(parent + key + ":", 
                                                        result[key],
                                                        print_output=print_output)
            else:                
                if int(result[key]['failed']):
                    if print_output:
                        print "%s%s: %s" % (parent, key, result[key].get('error', "No details provided"))
                    failed = True
        return failed

    def main(self):
        data = read_validator_config(files=[os.path.join(cfg_dir, 'validator.yaml')])

        result = {}
        for script in data.get(self.stage, {}).get(self.component, []):
            for dirpath in check_path:
                if os.path.exists(os.path.join(dirpath, script)):
                    return_val = run_script(os.path.join(dirpath, script))
                    result[script] = json.loads(return_val)
                    break
            if not result.has_key(script):
                self.log.error("script %s not found" % script) 

        if self.component == "CLC" and self.traverse:
            # describe-services or get from config file
            ds = DescribeServices(url='http://localhost:8773',)
            data = ds.main()
            hosts = []

            for service in data['serviceStatuses']:
                hostname = urllib.splitport(urlparse.urlparse(service['serviceId']['uri']).netloc)[0]
                status = service['localState']
                component_type = service['serviceId']['type'] 
                if component_map.get(component_type):
                    hosts.append((hostname, component_type, status))

            for host, component_type, status in hosts:
                # print "running sub-check: %s - %s - %s" % (host, component_type, args.stage)
                result['-'.join([host, component_type])] = run_remote(host, component_type, self.stage, traverse=self.traverse)

        elif self.component == "CC" and self.traverse:
            # describe nodes is a CLC call; get from config file
            # dn = DescribeNodes(url='http://localhost:8773',)
            # data = dn.main()
            for host in self.euca_conf["NODES"].split():
                result[host] = run_remote(host, "NC", self.stage)

        return result
