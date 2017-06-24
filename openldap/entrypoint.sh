#!/bin/bash
set -e

if [ ! -f /touched ]; then
    python /ldap/scripts/run.py
    touch /touched
fi

# ensure ntp always running after container start/restart
service ntp restart
exec gosu root /opt/symas/lib64/slapd -d 256 -u root -g root -h ldap://0.0.0.0:1389/ -f /opt/symas/etc/openldap/slapd.conf -F /opt/symas/etc/openldap/slapd.d
