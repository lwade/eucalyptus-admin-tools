eucalyptus-admin-tools
======================

The is a rewrite of the "eucadmin" package from the eucalyptus source tree.
This version relies on [requestbuilder](https://github.com/boto/requestbuilder)
rather than boto, argparse rather than optparse, and is designed to make
command classes callable from inside python.

In addition to better command-line help, this version also introduces
"euca-validator", a tool for inspecting various aspects of a cloud deployment.

## Quick start

### Assumptions

* Currently, this code is being tested on CentOS and RHEL 6.
* Required RPMs include:  python-requests python-six python-argparse
python-paramiko
* A requestbuilder RPM is available from
[gholms' cloud repo](http://repos.fedorapeople.org/repos/gholms/cloud/epel-6/x86_64/)
* As an alternative to using the RPMs above, you could simply use virtualenv

### Setup

Virtualenv setup is as follows:

* virtualenv --system-site-packages ~/venv-eucadmin
* source ~/venv-eucadmin/bin/activate
* git clone git@github.com:a13m/eucalyptus-admin-tools.git
* cd eucalyptus-admin-tools
* python setup.py install

Currently, euca-validator in "traverse" mode isn't very smart about running a 
remote validator correctly over ssh, so I'm using a helper script as 
/usr/bin/euca-validator:

```
#!/bin/sh

source ~/venv-eucadmin/bin/activate
export EUCALYPTUS=/opt/eucalyptus

euca-validator $@
```

### Writing a validator script

The current expectations of a script in the validator-scripts directory are:

* It runs on a single machine [1]
* It returns a valid JSON dictionary on stdout
* It should *not* alter the system in any way (don't get too pedantic here -- 
yes, every command alters the system.  No killing processes, modifying or
removing files, etc.)
* If the check succeeds, it should set "failed" to 0 in the dictionary.  Any
non-zero value is assumed to mean failure.
* If the script needs to do different things depending on the component being
checked, it may read the EUCA_ROLES environment variable, which should be
assumed to be a comma-separated list of component abbreviations (i.e., a subset
of CLC,WS,CC,SC,NC,UI).  As more components may be added later, unknown
components need to be dealt with gracefully (which could mean "ignored").
* Scripts not intended to run at "preinstall" may assume that $EUCALYPTUS is
set and that eucalyptus.conf is readable.

[1] There is an intent to allow for multi-machine validation scripts for things
like ensuring that all systems have the same network mode set.  The guidelines
for such scripts need to be discussed.
