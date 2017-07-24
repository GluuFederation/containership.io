#!/bin/bash
set -e

download_custom_tar() {
    if [ ! -z ${GLUU_CUSTOM_OXAUTH_URL} ]; then
        mkdir -p /tmp/oxauth
        wget -q ${GLUU_CUSTOM_OXAUTH_URL} -O /tmp/oxauth/custom-oxauth.tar.gz
        cd /tmp/oxauth
        tar xf custom-oxauth.tar.gz

        if [ -d /tmp/oxauth/pages ]; then
            cp -R /tmp/oxauth/pages/ /opt/gluu/jetty/oxauth/custom/
        fi

        if [ -d /tmp/oxauth/static ]; then
            cp -R /tmp/oxauth/static/ /opt/gluu/jetty/oxauth/custom/
        fi

        if [ -d /tmp/oxauth/lib/ext ]; then
            cp -R /tmp/oxauth/lib/ext/ /opt/gluu/jetty/oxauth/lib/
        fi
    fi
}

prepare_jks_sync_env() {
    echo "export GLUU_KV_HOST=${GLUU_KV_HOST}" > /opt/jks_sync/env
    echo "export GLUU_KV_PORT=${GLUU_KV_PORT}" >> /opt/jks_sync/env
}


if [ ! -f /touched ]; then
    download_custom_tar
    python /opt/scripts/entrypoint.py
    touch /touched
fi

# run JKS sync as background job
prepare_jks_sync_env
cron

cd /opt/gluu/jetty/oxauth
exec gosu root java -jar /opt/jetty/start.jar -server \
    -Xms256m -Xmx4096m -XX:+DisableExplicitGC \
    -Dgluu.base=/etc/gluu \
    -Dcatalina.base=/opt/gluu/jetty/oxauth \
    -Dpython.home=/opt/jython
