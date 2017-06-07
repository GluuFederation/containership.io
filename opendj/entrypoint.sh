#!/bin/bash
set -e

if [ ! -f /touched ]; then
    touch /touched
    python /gluu/script/run.py
fi


#run opendj process
exec gosu root /opt/opendj/bin/start-ds --quiet -N