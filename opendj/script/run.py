# -*- coding: utf-8 -*-
# Copyright (c) 2015 Gluu
#
# All rights reserved.
import os
import utils

import consulate

consul = consulate.Consul(host=GLUU_DATASTORE, port=GLUU_DATASTORE_PORT)

#ENV VARS
GLUU_DATASTORE = os.environ.get('GLUU_DATASTORE', 'localhost')
GLUU_DATASTORE_PORT = os.environ.get('GLUU_DATASTORE_PORT', 8500)
GLUU_REPLICATE_FROM = os.environ.get('GLUU_REPLICATE_FROM', None)
GLUU_REPLICATE_PORT = 8989

# LDAP
LDAP_BASE = '/opt/opendj'
LDAP_SETUP_CMD = '/opt/opendj/setup'
LDAP_DS_JAVA_PROP_COMMAND = '/opt/opendj/bin/dsjavaproperties'
LDAP_DSCONFIG_COMMAND = '/opt/opendj/bin/dsconfig'
LDAP_ADMIN_PORT = consul.kv.get('ldap_admin_port')
LDAP_BINDDN = consul.kv.get('ldap_binddn')
LDAP_PASS_FN = consul.kv.get('ldap_pass_fn') #TODO fix encoded pass, passkey and use pass file or not

#LDAP_ENCODED_PASS = consul.kv.get('ldap_encoded_pw')
#LDAP_PW_FILE_PATH = '/opt/gluu/garbage/secret/.pw'

def setup_opendj():
    """Setups OpenDJ server without actually running the server
    in post-installation step.
    """

    src = '/opt/gluu/opendj/templates/opendj-setup.properties'
    dest = os.path.join(LDAP_BASE, os.path.basename(src))
    ctx = {
        "ldap_hostname": consul.kv.get('ldap_hostname'),
        "ldap_port": consul.kv.get('ldap_port'),
        "ldaps_port": consul.kv.get('ldaps_port'),
        "ldap_jmx_port": consul.kv.get('ldap_jmx_port'),
        "ldap_admin_port": consul.kv.get('ldap_admin_port'),
        "ldap_binddn": consul.kv.get('ldap_binddn'),
        "ldap_pass_fn": consul.kv.get('ldap_pass_fn'), #TODO fix encoded pass, passkey and use pass file or not
        "ldap_backend_type": "je",  # OpenDJ 3.0
    }
    utils.render_template(src, dest, ctx)

    setup_cmd = " ".join([
        LDAP_SETUP_CMD,
        '--no-prompt', '--cli', '--doNotStart', '--acceptLicense',
        '--propertiesFilePath', dest,
    ])
    utils.po_run(setup_cmd)
    utils.po_run(LDAP_DS_JAVA_PROP_COMMAND)

def configure_opendj():
    #Configures OpenDJ.

    config_changes = [
        "set-global-configuration-prop --set single-structural-objectclass-behavior:accept",
        "set-attribute-syntax-prop --syntax-name 'Directory String' --set allow-zero-length-values:true",
        "set-password-policy-prop --policy-name 'Default Password Policy' --set allow-pre-encoded-passwords:true",
        "set-log-publisher-prop --publisher-name 'File-Based Audit Logger' --set enabled:true",
        "create-backend --backend-name site --set base-dn:o=site --type je --set enabled:true",  # OpenDJ 3.0
        "set-connection-handler-prop --handler-name 'LDAP Connection Handler' --set enabled:false",
        'set-access-control-handler-prop --remove global-aci:\'(targetattr!=\\"userPassword||authPassword||debugsearchindex||changes||changeNumber||changeType||changeTime||targetDN||newRDN||newSuperior||deleteOldRDN\\")(version 3.0; acl \\"Anonymous read access\\"; allow (read,search,compare) userdn=\\"ldap:///anyone\\";)\'',  # OpenDJ 3.0
        "set-global-configuration-prop --set reject-unauthenticated-requests:true",
        "set-password-policy-prop --policy-name 'Default Password Policy' --set default-password-storage-scheme:'Salted SHA-512'",
    ]

    for changes in config_changes:
        dsconfig_cmd = " ".join([
            self.LDAP_DSCONFIG_COMMAND,
            '--trustAll',
            '--no-prompt',
            '--hostname', 'localhost', #self.container.hostname, #TODO: fix me
            '--port', LDAP_ADMIN_PORT,
            '--bindDN', "'{}'".format(LDAP_BINDDN),
            '--bindPasswordFile', LDAP_PASS_FN,
            changes,
        ])

        dsconfig_cmd = '''sh -c "{}"'''.format(dsconfig_cmd) # whay we are using sh -c here
        utils.po_run(dsconfig_cmd)

def index_opendj(backend):
    #Creates required index in OpenDJ server.
    
    src = "/opt/gluu/opendj/static/opendj_index.json"
    with open(src, "r") as fp:
        data = fp.read()

    try:
        index_json = json.loads(data)
    except ValueError:
        self.logger.warn("unable to read JSON string from opendj_index.json")
        index_json = []

    for attr_map in index_json:
        attr_name = attr_map['attribute']

        for index_type in attr_map["index"]:
            for backend_name in attr_map["backend"]:
                if backend_name != backend:
                    continue

                index_cmd = " ".join([
                    LDAP_DSCONFIG_COMMAND,
                    "create-backend-index",
                    '--backend-name', backend,
                    '--type', 'generic',
                    '--index-name', attr_name,
                    '--set', 'index-type:%s' % index_type,
                    '--set', 'index-entry-limit:4000',
                    '--hostName', 'localhost', #self.container.hostname, #TODO: fix me
                    '--port', LDAP_ADMIN_PORT,
                    '--bindDN', "'{}'".format(LDAP_BINDDN),
                    '-j', LDAP_PASS_FN,
                    '--trustAll', '--noPropertiesFile', '--no-prompt',
                ])
                utils.po_run(index_cmd)

def replicate(peer):
    """Setups a replication between two OpenDJ servers.

    The data will be replicated from existing OpenDJ server.

    :param peer: OpenDJ server where the initial data
                          will be replicated from.
    """

    #setup_obj = LdapSetup(peer, self.cluster,
    #                      self.app, logger=self.logger)

    # creates temporary password file
    #setup_obj.write_ldap_pw()

    base_dns = ("o=gluu", "o=site",)

    # self.logger.info("initializing and enabling replication between {} and {}".format(
    #     peer.hostname, self.container.hostname,
    # ))
    for base_dn in base_dns:
        enable_cmd = " ".join([
            "/opt/opendj/bin/dsreplication", "enable",
            "--host1", peer.hostname, #TODO: how to get peer host name
            "--port1", LDAP_ADMIN_PORT,
            "--bindDN1", "'{}'".format(LDAP_BINDDN),
            "--bindPasswordFile1", LDAP_PASS_FN,
            "--replicationPort1", GLUU_REPLICATE_PORT,
            "--host2", 'localhost', #self.container.hostname, #TODO: fix me
            "--port2", LDAP_ADMIN_PORT,
            "--bindDN2", "'{}'".format(LDAP_BINDDN),
            "--bindPasswordFile2", LDAP_PASS_FN,
            "--replicationPort2", GLUU_REPLICATE_PORT,
            "--adminUID", "admin",
            "--adminPasswordFile", LDAP_PASS_FN,
            "--baseDN", "'{}'".format(base_dn),
            "--secureReplication1", "--secureReplication2",
            "-X", "-n", "-Q",
        ])
        utils.po_run(enable_cmd)

        # wait before initializing the replication to ensure it
        # has been enabled
        time.sleep(10)

        init_cmd = " ".join([
            "/opt/opendj/bin/dsreplication", "initialize",
            "--baseDN", "'{}'".format(base_dn),
            "--adminUID", "admin",
            "--adminPasswordFile", LDAP_PASS_FN,
            "--hostSource", peer.hostname, #TODO: how to get peer host name
            "--portSource", LDAP_ADMIN_PORT,
            "--hostDestination", 'localhost', #self.container.hostname, #TODO: fix me
            "--portDestination", LDAP_ADMIN_PORT,
            "-X", "-n", "-Q",
        ])
        utils.po_run(init_cmd)
        time.sleep(5)

def store_pw():
    with open(LDAP_PW_FILE_PATH, 'w') as fp:
        fp.write(LDAP_ENCODED_PASS)

def del_pw():
    if os.path.isfile(LDAP_PW_FILE_PATH):
        os.remove(LDAP_PW_FILE_PATH)

def run():
    store_pw()
    setup_opendj()
    configure_opendj()
    index_opendj("site")
    index_opendj("userRoot")
    replicate()
    del_pw()


if __name__ == '__main__':
    run()
