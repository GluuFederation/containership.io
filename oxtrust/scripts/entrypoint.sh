#!/bin/bash
set -e

if [ ! -f /touched ]; then
    touch /touched
    # TODO:
    # 1. render /etc/gluu/conf/salt.tmpl
    # 2. render /etc/gluu/conf/ox-ldap.properties.tmpl
fi

cd /opt/gluu/jetty/identity
exec java -jar /opt/jetty/start.jar -server -Xms256m -Xmx2048m -XX:+DisableExplicitGC -Dgluu.base=/etc/gluu -Dcatalina.base=/opt/gluu/jetty/identity -Dorg.eclipse.jetty.server.Request.maxFormContentSize=50000000 -Dpython.home=/opt/jython
