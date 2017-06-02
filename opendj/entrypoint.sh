#!/bin/bash
set -e

if [ ! -f /touched ]; then
    touch /touched
    python /opt/script/run.py
fi


#run opendj process
#TODO: fix it, need to run it in forground mode
exec gosu root /opt/opendj/bin/start-ds --quiet -N