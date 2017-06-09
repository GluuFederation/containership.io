#!/bin/bash
set -e

if [ ! -f /touched ]; then
    touch /touched
    python /ldap/scripts/run.py
fi


#run openldap process
exec gosu root /opt/symas/lib64/slapd -d 32768 -u root -g root -h ldap://127.0.0.1:1389/