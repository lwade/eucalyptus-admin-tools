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

### Running euca-validator

euca-validator currently has four "stages".  They are still up for discussion,
but it made sense to me that these might be distinct check points:

* preinstall -- This is for checks which can be done on a system before
eucalyptus itself is installed.
* postinstall -- This is for checks of the eucalyptus configuration after
installation, but before component registration.
* registration -- This is for checks which may be done when a component is
being registered.  The euca-register-* commands will eventually run these
checks automatically.
* monitor -- These checks are for ongoing monitoring of a running cloud.

Additionally, euca-validator has two basic modes of operation: single-machine
mode (the default), and "traverse" mode.  In single-machine mode, all checks
are confined to a single component on the system.  In "traverse" mode, 
multi-machine checks may be done, and the validator will rerun itself on
other component systems as well (the CLC will execute a validator on each SC, 
Walrus, and CC will execute a validator on each NC).

Currently, checks in "traverse" mode use "describe" calls to locate other
components in the cloud.  The intent is to also allow the user to specify
an _expected_ topology of their cloud, in which case the validator should also
report any discrepancies.

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
