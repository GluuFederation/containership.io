#!/bin/bash
set -e

import_ssl_cert() {
    if [ -f /etc/certs/gluu_https.crt ]; then
        openssl x509 -outform der -in /etc/certs/gluu_https.crt -out /etc/certs/gluu_https.der
        keytool -importcert -trustcacerts \
            -alias gluu_https \
            -file /etc/certs/gluu_https.der \
            -keystore /usr/lib/jvm/default-java/jre/lib/security/cacerts \
            -storepass changeit \
            -noprompt
    fi
}

if [ ! -f /touched ]; then
    touch /touched
    python /opt/scripts/entrypoint.py
    import_ssl_cert
fi

cd /opt/gluu/jetty/identity
exec java -jar /opt/jetty/start.jar -server -Xms256m -Xmx2048m -XX:+DisableExplicitGC -Dgluu.base=/etc/gluu -Dcatalina.base=/opt/gluu/jetty/identity -Dorg.eclipse.jetty.server.Request.maxFormContentSize=50000000 -Dpython.home=/opt/jython
