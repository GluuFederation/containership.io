#!/bin/bash
set -e

if [ ! -f /touched ]; then
    touch /touched
    python /opt/scripts/entrypoint.py
fi

cd /opt/gluu/jetty/oxauth
exec java -jar /opt/jetty/start.jar -server -Xms256m -Xmx4096m -XX:+DisableExplicitGC -Dgluu.base=/etc/gluu -Dcatalina.base=/opt/gluu/jetty/oxauth -Dpython.home=/opt/jython
