import base64
import glob
import os
import shutil
import subprocess
import traceback
import tempfile
import logging

import consulate
from M2Crypto.EVP import Cipher


GLUU_KV_HOST = os.environ.get('GLUU_KV_HOST', 'localhost')
GLUU_KV_PORT = os.environ.get('GLUU_KV_PORT', 8500)
# Whether initial data should be inserted
GLUU_LDAP_INIT = os.environ.get("GLUU_LDAP_INIT", True)
GLUU_LDAP_INIT_HOST = os.environ.get('GLUU_LDAP_INIT_HOST', 'localhost')
GLUU_LDAP_INIT_PORT = os.environ.get("GLUU_LDAP_INIT_PORT", 1389)
TMPDIR = tempfile.mkdtemp()

consul = consulate.Consul(host=GLUU_KV_HOST, port=GLUU_KV_PORT)

logger = logging.getLogger("ldap_initializer")
logger.setLevel(logging.INFO)
ch = logging.FileHandler('/ldap/ldap_initializer.log')
fmt = logging.Formatter('[%(levelname)s] - %(asctime)s - %(message)s')
ch.setFormatter(fmt)
logger.addHandler(ch)


def as_boolean(val, default=False):
    truthy = set(('t', 'T', 'true', 'True', 'TRUE', '1', 1, True))
    falsy = set(('f', 'F', 'false', 'False', 'FALSE', '0', 0, False))

    if val in truthy:
        return True
    if val in falsy:
        return False
    return default


def runcmd(args, cwd=None, env=None, useWait=False):
    try:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=env)
        if useWait:
            code = p.wait()
            logger.info('Run: %s with result code: %d' % (' '.join(args), code))
        else:
            output, err = p.communicate()
            if output:
                logger.info(output)
            if err:
                logger.warn(err)

    except:
        logger.warn('Error running command : %s' % ' '.join(args))
        logger.warn(traceback.format_exc())


def render_ldif():
    ctx_data = {
        # o_site.ldif
        # has no variables

        # appliance.ldif
        'ldap_use_ssl': consul.kv.get('ldap_use_ssl'),
        # oxpassport-config.ldif
        'inumAppliance': consul.kv.get('inumAppliance'),
        'ldap_hostname': consul.kv.get('ldap_init_host'),
        # TODO: currently using std ldaps port 1636 as ldap port.
        # after basic testing we need to do it right, and remove this hack.
        # to do this properly we need to update all templates.
        'ldaps_port': consul.kv.get('ldap_init_port'),
        'ldap_binddn': consul.kv.get('ldap_binddn'),
        'encoded_ox_ldap_pw': consul.kv.get('encoded_ox_ldap_pw'),
        'jetty_base': consul.kv.get('jetty_base'),

        # asimba.ldif
        # attributes.ldif
        # groups.ldif
        # oxidp.ldif
        # scopes.ldif
        'inumOrg': r"{}".format(consul.kv.get('inumOrg')),  # raw string

        # base.ldif
        'orgName': consul.kv.get('orgName'),

        # clients.ldif
        'oxauth_client_id': consul.kv.get('oxauth_client_id'),
        'oxauthClient_encoded_pw': consul.kv.get('oxauthClient_encoded_pw'),
        'hostname': consul.kv.get('hostname'),

        # configuration.ldif
        'oxauth_config_base64': consul.kv.get('oxauth_config_base64'),
        'oxauth_static_conf_base64': consul.kv.get('oxauth_static_conf_base64'),
        'oxauth_openid_key_base64': consul.kv.get('oxauth_openid_key_base64'),
        'oxauth_error_base64': consul.kv.get('oxauth_error_base64'),
        'oxtrust_config_base64': consul.kv.get('oxtrust_config_base64'),
        'oxtrust_cache_refresh_base64': consul.kv.get('oxtrust_cache_refresh_base64'),
        'oxtrust_import_person_base64': consul.kv.get('oxtrust_import_person_base64'),
        'oxidp_config_base64': consul.kv.get('oxidp_config_base64'),
        'oxcas_config_base64': consul.kv.get('oxcas_config_base64'),
        'oxasimba_config_base64': consul.kv.get('oxasimba_config_base64'),

        # passport.ldif
        'passport_rs_client_id': consul.kv.get('passport_rs_client_id'),
        'passport_rs_client_base64_jwks': consul.kv.get('passport_rs_client_base64_jwks'),
        'passport_rp_client_id': consul.kv.get('passport_rp_client_id'),
        'passport_rp_client_base64_jwks': consul.kv.get('passport_rp_client_base64_jwks'),

        # people.ldif
        "encoded_ldap_pw": consul.kv.get('encoded_ldap_pw'),

        # scim.ldif
        'scim_rs_client_id': consul.kv.get('scim_rs_client_id'),
        'scim_rs_client_base64_jwks': consul.kv.get('scim_rs_client_base64_jwks'),
        'scim_rp_client_id': consul.kv.get('scim_rp_client_id'),
        'scim_rp_client_base64_jwks': consul.kv.get('scim_rp_client_base64_jwks'),

        # scripts.ldif
        # already covered at this point

        # replication.ldif
        'replication_dn': consul.kv.get('replication_dn'),
        'replication_cn': consul.kv.get('replication_cn'),
        'encoded_replication_pw': consul.kv.get('encoded_replication_pw'),
    }

    ldif_template_base = '/ldap/templates/ldif'
    pattern = '/*.ldif'
    for file_path in glob.glob(ldif_template_base + pattern):
        with open(file_path, 'r') as fp:
            template = fp.read()
        # render
        rendered_content = template % ctx_data
        # write to tmpdir
        with open(os.path.join(TMPDIR, os.path.basename(file_path)), 'w') as fp:
            fp.write(rendered_content)


def import_ldif():
    ldif_import_order = [
        'base.ldif',
        'appliance.ldif',
        'attributes.ldif',
        'scopes.ldif',
        'clients.ldif',
        'people.ldif',
        'groups.ldif',
        'o_site.ldif',
        'scripts.ldif',
        'configuration.ldif',
        'scim.ldif',
        'asimba.ldif',
        'passport.ldif',
        'oxpassport-config.ldif',
        'oxidp.ldif',
        "replication.ldif",
    ]

    slapadd_cmd = '/opt/symas/bin/slapadd'
    config = '/opt/symas/etc/openldap/slapd.conf'

    for ldif_file in ldif_import_order:
        ldif_file_path = os.path.join(TMPDIR, ldif_file)
        if 'site.ldif' in ldif_file_path:
            runcmd([slapadd_cmd, '-b', 'o=site', '-f', config, '-l', ldif_file_path])
        else:
            runcmd([slapadd_cmd, '-b', 'o=gluu', '-f', config, '-l', ldif_file_path])


def import_custom_schema():
    base_path = '/ldap/custom_schema'
    pattern = '/*.ldif'
    slapadd_cmd = '/opt/symas/bin/slapadd'
    config = '/opt/symas/etc/openldap/slapd.conf'

    for file_path in glob.glob(base_path + pattern):
        runcmd([slapadd_cmd, '-b', 'o=gluu', '-f', config, '-l', file_path])


def cleanup():
    shutil.rmtree(TMPDIR)


# TODO: Remove oxtrust related code from openldap
def reindent(text, num_spaces=1):
    text = [(num_spaces * " ") + line.lstrip() for line in text.splitlines()]
    text = "\n".join(text)
    return text


def generate_base64_contents(text, num_spaces=1):
    text = text.encode("base64").strip()
    if num_spaces > 0:
        text = reindent(text, num_spaces)
    return text


def oxtrust_config():
    # keeping redundent data in context of ldif ctx_data dict for now.
    # so that we can easily remove it from here
    ctx = {
        'inumOrg': r"{}".format(consul.kv.get('inumOrg')),  # raw string
        'admin_email': consul.kv.get('admin_email'),
        'inumAppliance': consul.kv.get('inumAppliance'),
        'hostname': consul.kv.get('hostname'),
        'shibJksFn': consul.kv.get('shibJksFn'),
        'shibJksPass': consul.kv.get('shibJksPass'),
        'jetty_base': consul.kv.get('jetty_base'),
        'oxTrustConfigGeneration': consul.kv.get('oxTrustConfigGeneration'),
        'encoded_shib_jks_pw': consul.kv.get('encoded_shib_jks_pw'),
        'oxauth_client_id': consul.kv.get('oxauth_client_id'),
        'oxauthClient_encoded_pw': consul.kv.get('oxauthClient_encoded_pw'),
        'scim_rs_client_id': consul.kv.get('scim_rs_client_id'),
        'scim_rs_client_jks_fn': consul.kv.get('scim_rs_client_jks_fn'),
        'scim_rs_client_jks_pass_encoded': consul.kv.get('scim_rs_client_jks_pass_encoded'),
        'passport_rs_client_id': consul.kv.get('passport_rs_client_id'),
        'passport_rs_client_jks_fn': consul.kv.get('passport_rs_client_jks_fn'),
        'passport_rs_client_jks_pass_encoded': consul.kv.get('passport_rs_client_jks_pass_encoded'),
        'shibboleth_version': consul.kv.get('shibboleth_version'),
        'idp3Folder': consul.kv.get('idp3Folder'),
        'orgName': consul.kv.get('orgName'),
        'ldap_site_binddn': consul.kv.get('ldap_site_binddn'),
        'encoded_ox_ldap_pw': consul.kv.get('encoded_ox_ldap_pw'),
        'ldap_hostname': consul.kv.get('ldap_init_host'),
        'ldaps_port': consul.kv.get('ldap_init_port'),
    }

    oxtrust_template_base = '/ldap/templates/oxtrust'

    key_and_jsonfile_map = {
        'oxtrust_cache_refresh_base64': 'oxtrust-cache-refresh.json',
        'oxtrust_config_base64': 'oxtrust-config.json',
        'oxtrust_import_person_base64': 'oxtrust-import-person.json'
    }

    for key, json_file in key_and_jsonfile_map.iteritems():
        json_file_path = os.path.join(oxtrust_template_base, json_file)
        with open(json_file_path, 'r') as fp:
            consul.kv.set(key, generate_base64_contents(fp.read() % ctx))


def run():
    if as_boolean(GLUU_LDAP_INIT):
        consul.kv.set('ldap_init_host', GLUU_LDAP_INIT_HOST)
        consul.kv.set('ldap_init_port', GLUU_LDAP_INIT_PORT)
        consul.kv.set("oxTrustConfigGeneration", False)

        oxtrust_config()
        logger.info('start rendering of ldif files')
        render_ldif()
        logger.info('start importing rendered ldif files')
        import_ldif()
        logger.info('start importing custom ldif file')
        import_custom_schema()
    cleanup()


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


if __name__ == '__main__':
    run()
