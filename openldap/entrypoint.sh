#!/bin/bash
set -e

if [ ! -f /touched ]; then
    python /ldap/scripts/run.py
    touch /touched
fi

# TODO: should we use supervisor to manage ntpd and atd?

# ensure ntp always running after container start/restart
service ntp restart

# ensure atd always running after container start/restart
service atd restart

# delay replication check 1 minute from now
at now +1 minute -f /ldap/scripts/replicator.sh

# run slapd
exec gosu root /opt/symas/lib64/slapd -d 256 -u root -g root -h ldap://0.0.0.0:1389/ -f /opt/symas/etc/openldap/slapd.conf -F /opt/symas/etc/openldap/slapd.d
