#!/bin/bash
set -e

download_custom_schema() {
    if [ ! -z ${GLUU_CUSTOM_SCHEMA_URL} ]; then
        wget -q ${GLUU_CUSTOM_SCHEMA_URL} -O /ldap/custom_schema/custom-schema.tar.gz
        cd /ldap/custom_schema
        tar xf custom-schema.tar.gz
    fi
}

if [ ! -f /ldap/touched ]; then
    python /ldap/scripts/ldap_configurator.py
    touch /ldap/touched
fi

mkdir -p /ldap/flag
if [ ! -f /ldap/flag/ldap_initialized ]; then
    download_custom_schema
    python /ldap/scripts/ldap_initializer.py
    touch /ldap/flag/ldap_initialized
fi

# ensure ntp always running after container start/restart
# service ntp restart > /dev/null

# run replication as background job
nohup /ldap/scripts/replicator.sh >>/ldap/replicator.log 2>&1&

# run slapd
exec /opt/symas/lib64/slapd \
    -d 256 \
    -u gluu \
    -g gluu \
    -h ldap://0.0.0.0:1389/ \
    -f /opt/symas/etc/openldap/slapd.conf \
    -F /opt/symas/etc/openldap/slapd.d
