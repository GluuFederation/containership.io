#!/bin/bash
set -e

if [ ! -f /touched ]; then
    touch /touched
    # TODO:
    # 1. render /etc/gluu/conf/salt.tmpl
    # 2. render /etc/gluu/conf/ox-ldap.properties.tmpl
fi

cd /opt/gluu/jetty/oxauth
exec java -jar /opt/jetty/start.jar -server -Xms256m -Xmx4096m -XX:+DisableExplicitGC -Dgluu.base=/etc/gluu -Dcatalina.base=/opt/gluu/jetty/oxauth -Dpython.home=/opt/jython
