#!/bin/bash
set -e

if [ ! -f /touched ]; then
    touch /touched
    python /ldap/scripts/run.py
fi


#run openldap process
# TODO: currently using port 1636 but will change to 1389
exec gosu root /opt/symas/lib64/slapd -d 32768 -u root -g root -h ldap://0.0.0.0:1389/
