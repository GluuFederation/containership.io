#!/bin/bash
set -e

if [ ! -f /touched ]; then
    touch /touched
    python /opt/scripts/entrypoint.py
fi

exec /usr/sbin/nginx -g "daemon off;"
