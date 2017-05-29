#!/bin/bash
set -e

if [ ! -f /touched ]; then
    touch /touched
    python /opt/script/run.py
fi


#run opendj process
#exec gosu root /path/of/opendj