eucalyptus-admin-tools
======================

The is a rewrite of the "eucadmin" package from the eucalyptus source tree.  This version relies on [requestbuilder](https://github.com/boto/requestbuilder) rather than boto, argparse rather than optparse, and is designed to make command classes callable from inside python.

In addition to better command-line help, this version also introduces "euca-validator", a tool for inspecting various aspects of a cloud deployment.

## Quick start

### Assumptions

* Currently, this code is being tested on CentOS and RHEL 6.
* Required RPMs include:  python-requests python-six python-argparse python-paramiko

### Get the code

```
BASEDIR=${HOME}/py
mkdir -p $BASEDIR
cd ${BASEDIR}
git clone git://github.com/boto/requestbuilder.git
git clone git://github.com/a13m/eucalyptus-admin-tools.git
export PYTHONPATH=${BASEDIR}/requestbuilder:${BASEDIR}/eucalyptus-admin-tools
export PATH=${BASEDIR}/eucalyptus-admin-tools/bin:$PATH
```

Note that the suggested PATH ordering there is for superseding other eucalyptus-admin-tools installations on your system.

Currently, euca-validator in "traverse" mode isn't very smart about running a remote validator correctly over ssh, so I'm using a helper script as /usr/bin/euca-validator:

```
#!/bin/sh

BASEDIR=/home/agrimm/py
export EUCALYPTUS=/opt/eucalyptus
export PYTHONPATH=${BASEDIR}/requestbuilder:${BASEDIR}/eucalyptus-admin-tools
export EUCADMIN_CONF_DIR=${BASEDIR}/eucalyptus-admin-tools/config
export EUCADMIN_DATA_DIR=${BASEDIR}/eucalyptus-admin-tools

${BASEDIR}/eucalyptus-admin-tools/bin/euca-validator $@
```

Hopefully I'll be cleaning up the config & data path searches soon to make this unnecessary.

Lots of TODO items here.  The package doesn't even have a proper setup.py yet.  Stay tuned.
