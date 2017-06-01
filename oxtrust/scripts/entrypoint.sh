#!/bin/bash
set -e

if [ ! -f /touched ]; then
    touch /touched
    python /opt/scripts/entrypoint.py
fi

cd /opt/gluu/jetty/identity
exec java -jar /opt/jetty/start.jar -server -Xms256m -Xmx2048m -XX:+DisableExplicitGC -Dgluu.base=/etc/gluu -Dcatalina.base=/opt/gluu/jetty/identity -Dorg.eclipse.jetty.server.Request.maxFormContentSize=50000000 -Dpython.home=/opt/jython
