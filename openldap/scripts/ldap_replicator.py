import base64
import json
import logging
import os
import re
from collections import namedtuple
from contextlib import contextmanager

import consulate
import ldap
from ldap.modlist import modifyModlist
from M2Crypto.EVP import Cipher

OLC_RGX = re.compile("^olcDatabase")

OLCSYNCREPL_TMPL = """rid={replication_id} provider={protocol}://{peer_host}:{peer_port} bindmethod=simple binddn="{replication_dn}" credentials={replication_pw} searchbase="o=gluu" schemachecking=on type=refreshAndPersist retry="60 +" logbase="cn=accesslog" logfilter="(&(objectClass=auditWriteObject)(reqResult=0))" syncdata=accesslog"""

LDAPServer = namedtuple(
    "LDAPServer",
    ["server_id", "host", "port", "active"]
)

kv_host = os.environ.get("GLUU_KV_HOST", "localhost")
kv_port = os.environ.get("GLUU_KV_PORT", 8500)
check_interval = os.environ.get("GLUU_LDAP_CHECK_INTERVAL", 30)
check_logfile = os.environ.get("GLUU_LDAP_CHECK_LOGFILE", "/var/log/replicator.log")
consul = consulate.Consul(host=kv_host, port=kv_port)

logger = logging.getLogger("ldap_replicator")
logger.setLevel(logging.INFO)
ch = logging.FileHandler(check_logfile)
fmt = logging.Formatter('[%(levelname)s] - %(asctime)s - %(message)s')
ch.setFormatter(fmt)
logger.addHandler(ch)


def decrypt_text(encrypted_text, key):
    # Porting from pyDes-based encryption (see http://git.io/htpk)
    # to use M2Crypto instead (see https://gist.github.com/mrluanma/917014)
    cipher = Cipher(alg="des_ede3_ecb",
                    key=b"{}".format(key),
                    op=0,
                    iv="\0" * 16)
    decrypted_text = cipher.update(base64.b64decode(
        b"{}".format(encrypted_text)
    ))
    decrypted_text += cipher.final()
    return decrypted_text


@contextmanager
def ldap_conn(host, port, user, passwd, protocol="ldap", starttls=False):
    try:
        conn = ldap.initialize("{}://{}:{}".format(
            protocol, host, port
        ))
        if starttls:
            conn.start_tls_s()
        conn.bind_s(user, passwd)
        yield conn
    except ldap.LDAPError:
        raise
    finally:
        conn.unbind()


def get_olcdb_entry(result):
    for r in result:
        if OLC_RGX.match(r[0]):
            if "olcSuffix" in r[1] and "o=gluu" in r[1]["olcSuffix"]:
                return r[0], r[1]
    return "", ""


def multi_master_syncrepl(servers, user, passwd, replication_dn,
                          replication_pw):
    servers = servers or []

    olcsyncrepl_map = {
        "{}:{}".format(server.host, server.port): OLCSYNCREPL_TMPL.format(
            replication_id=server.server_id,
            peer_host=server.host,
            peer_port=server.port,
            replication_dn=replication_dn,
            replication_pw=replication_pw,
            protocol="ldap",
        ) for server in servers
    }

    for server in servers:
        # exclude syncrepl pointing to current server
        olcsyncrepl = [
            syncrepl
            for provider, syncrepl in olcsyncrepl_map.iteritems()
            if "{}:{}".format(server.host, server.port) != provider
        ]

        try:
            with ldap_conn(server.host, server.port, user, passwd) as conn:
                modify_olcsyncrepl(conn, server, olcsyncrepl)
                modify_mirrormode(conn, server)
        except (ldap.TYPE_OR_VALUE_EXISTS, ldap.INAPPROPRIATE_MATCHING, ldap.SERVER_DOWN) as exc:
            logger.warn("unable to modify entries at {}:{}; reason={}".format(
                server.host, server.port, exc
            ))


def modify_olcserver(conn, server, server_id):
    result = conn.search_s("cn=config", ldap.SCOPE_BASE)
    dn, dbconfig = result[0]

    if "olcServerID" in dbconfig:
        modlist = modifyModlist(
            {"olcServerID": dbconfig["olcServerID"]},
            {"olcServerID": server_id},
        )
    else:
        modlist = [
            (ldap.MOD_ADD, "olcServerID", server_id),
        ]

    logger.info(
        "assigning server ID in {}:{}".format(server.host, server.port)
    )
    conn.modify_s(dn, modlist)


def modify_olcsyncrepl(conn, server, olcsyncrepl):
    # search for syncrepl
    result = conn.search_s("cn=config", ldap.SCOPE_SUBTREE,
                           "(objectClass=olcMdbConfig)", [])
    dn, dbconfig = get_olcdb_entry(result)

    # update syncrepl
    if "olcSyncrepl" in dbconfig:
        modlist = modifyModlist(
            {"olcSyncrepl": dbconfig["olcSyncrepl"]},  # old
            {"olcSyncrepl": olcsyncrepl},  # new
        )
    else:
        modlist = [
            (ldap.MOD_ADD, "olcSyncrepl", olcsyncrepl),
        ]
    logger.info(
        "enabling syncrepl in {}:{}".format(server.host, server.port)
    )
    conn.modify_s(dn, modlist)


def modify_mirrormode(conn, server, mode="TRUE"):
    # search for mirrormode
    result = conn.search_s("cn=config", ldap.SCOPE_SUBTREE,
                           "(objectClass=olcMdbConfig)", [])
    dn, dbconfig = get_olcdb_entry(result)

    # update mirrormode
    if "olcMirrorMode" in dbconfig:
        modlist = modifyModlist(
            {"olcMirrorMode": dbconfig["olcMirrorMode"]},  # old
            {"olcMirrorMode": [mode]},  # new
        )
    else:
        modlist = [(ldap.MOD_ADD, "olcMirrorMode", [mode])]
    logger.info(
        "enabling mirror in {}:{}".format(server.host, server.port)
    )
    conn.modify_s(dn, modlist)


def get_active_servers(max_num=4):
    servers = _get_servers_from_catalog(max_num)
    if not servers:
        servers = _get_servers_from_kv()
    return servers


def _get_servers_from_catalog(max_num=4):
    active_servers = []
    server_id = 1

    for server in consul.catalog.service("ldap-master"):
        active_servers.append(LDAPServer(
            server_id=server_id,
            host=server["Address"],
            port=server["ServicePort"],
            active=True,
        ))
        if len(active_servers) == max_num:
            break
        server_id += 1
    return active_servers


def _get_servers_from_kv(max_num=4):
    active_servers = []
    servers = [
        json.loads(master)
        for master in consul.kv.find("ldap_masters", []).values()
    ]

    user = "cn=directory manager,o=gluu"
    passwd = decrypt_text(consul.kv.get("encoded_ox_replication_pw"),
                          consul.kv.get("encoded_salt"))
    server_id = 1

    for server in servers:
        try:
            with ldap_conn(server["host"], server["port"], user, passwd):
                active_servers.append(LDAPServer(
                    server_id=server_id,
                    host=server["host"],
                    port=server["port"],
                    active=True,
                ))
                if len(active_servers) == max_num:
                    break
                server_id += 1
        except ldap.SERVER_DOWN as exc:
            logger.warn("excluding server {}:{}; reason={}".format(
                server["host"], server["port"], exc
            ))
            continue
    return active_servers


if __name__ == "__main__":
    logger.info("checking active servers")
    active_servers = get_active_servers()

    servers_num = len(active_servers)

    if not servers_num:
        logger.warn(
            "no active server(s) found ... skipping replication"
        )
    elif servers_num < 2:
        logger.warn(
            "active servers less than 2 instances ... "
            "skipping replication"
        )
    else:
        logger.info(
            "found {} active servers ... "
            "preparing replication".format(servers_num)
        )
        multi_master_syncrepl(
            active_servers,
            "cn=admin,cn=config",
            decrypt_text(consul.kv.get("encoded_ox_replication_pw"),
                         consul.kv.get("encoded_salt")),
            "cn=replicator,o=gluu",
            "secret",
        )
        logger.info("replication done")
