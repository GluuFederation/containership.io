import fcntl
import logging
import os
import socket
import struct

import consulate

GLUU_KV_HOST = os.environ.get('GLUU_KV_HOST', 'localhost')
GLUU_KV_PORT = os.environ.get('GLUU_KV_PORT', 8500)

consul = consulate.Consul(host=GLUU_KV_HOST, port=GLUU_KV_PORT)

logger = logging.getLogger("ldap_configurator")
logger.setLevel(logging.INFO)
ch = logging.FileHandler('/ldap/ldap_configurator.log')
fmt = logging.Formatter('[%(levelname)s] - %(asctime)s - %(message)s')
ch.setFormatter(fmt)
logger.addHandler(ch)


def get_ip_addr(ifname):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = socket.inet_ntoa(fcntl.ioctl(
        sock.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
    return addr


def guess_ip_addr():
    addr = ""

    # priorities
    for ifname in ("eth1", "eth0", "wlan0"):
        try:
            addr = get_ip_addr(ifname)
        except IOError:
            continue
        else:
            break
    return addr


# def get_id():
#     ctid = consul.kv.get('ctid') or 0
#     ctid = int(ctid)
#     consul.kv.set('ctid', ctid + 1)
#     return ctid


def configure_provider_openldap():
    src = '/ldap/templates/slapd/provider.conf'
    dest = '/opt/symas/etc/openldap/slapd.conf'

    # nid = get_id()
    ctx_data = {
        'openldapSchemaFolder': '/opt/gluu/schema/openldap',
        'encoded_ldap_pw': consul.kv.get('encoded_ldap_pw'),
        'replication_dn': consul.kv.get('replication_dn'),
        # 'server_id': nid,
    }

    with open(src, 'r') as fp:
        slapd_template = fp.read()

    with open(dest, 'w') as fp:
        fp.write(slapd_template % ctx_data)

    # register master
    host = guess_ip_addr()
    port = consul.kv.get("ldap_port", 1389)
    consul.kv.set("ldap_masters/{}:{}".format(host, port), {
        "host": host, "port": port,
    })


if __name__ == "__main__":
    logger.info('start of basic configuration')
    configure_provider_openldap()
