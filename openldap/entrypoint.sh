#!/bin/bash
set -e

if [ ! -f /touched ]; then
    python /ldap/scripts/run.py
    touch /touched
fi

# TODO: should we use supervisor to manage ntpd?

# ensure ntp always running after container start/restart
service ntp restart

# run replication as background job
nohup /ldap/scripts/replicator.sh >>/var/log/replicator.log 2>&1&

# run slapd
exec gosu root /opt/symas/lib64/slapd \
    -d 256 \
    -u root \
    -g root \
    -h ldap://0.0.0.0:1389/ \
    -f /opt/symas/etc/openldap/slapd.conf \
    -F /opt/symas/etc/openldap/slapd.d
