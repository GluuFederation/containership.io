#!/bin/bash
set -e

echo "Preparing env ..."

echo "export GLUU_KV_HOST=${GLUU_KV_HOST}" > /opt/key-rotation/env
echo "export GLUU_KV_PORT=${GLUU_KV_PORT}" >> /opt/key-rotation/env
echo "export GLUU_LDAP_URL=${GLUU_LDAP_URL}" >> /opt/key-rotation/env
echo "export GLUU_KEY_ROTATION_INTERVAL=${GLUU_KEY_ROTATION_INTERVAL}" >> /opt/key-rotation/env

echo "Running cron job ..."
echo ""

# run cron daemon
cron

exec tail -f /var/log/key-rotation.log
