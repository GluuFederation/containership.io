#!/bin/bash
set -e

enable_gluu_https() {
    if [ -f /etc/nginx/sites-available/gluu_https.conf ]; then
        ln -sf /etc/nginx/sites-available/gluu_https.conf /etc/nginx/sites-enabled/gluu_https.conf
        rm /etc/nginx/sites-enabled/default
    fi

}

if [ ! -f /touched ]; then
    touch /touched
    python /opt/scripts/entrypoint.py
    enable_gluu_https
fi

exec gosu root /usr/sbin/nginx -g "daemon off;"
