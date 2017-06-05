import base64
import hashlib
import os
import random
import string
import uuid

import click
import consulate
from M2Crypto.EVP import Cipher


# Default charset
_DEFAULT_CHARS = "".join([string.ascii_uppercase,
                          string.digits,
                          string.lowercase])


def get_random_chars(size=12, chars=_DEFAULT_CHARS):
    """Generates random characters.
    """
    return ''.join(random.choice(chars) for _ in range(size))


def ldap_encode(password):
    # borrowed from community-edition-setup project
    # see http://git.io/vIRex
    salt = os.urandom(4)
    sha = hashlib.sha1(password)
    sha.update(salt)
    b64encoded = '{0}{1}'.format(sha.digest(), salt).encode('base64').strip()
    encrypted_password = '{{SSHA}}{0}'.format(b64encoded)
    return encrypted_password


def get_quad():
    # borrowed from community-edition-setup project
    # see http://git.io/he1p
    return str(uuid.uuid4())[:4].upper()


def encrypt_text(text, key):
    # Porting from pyDes-based encryption (see http://git.io/htxa)
    # to use M2Crypto instead (see https://gist.github.com/mrluanma/917014)
    cipher = Cipher(alg="des_ede3_ecb",
                    key=b"{}".format(key),
                    op=1,
                    iv="\0" * 16)
    encrypted_text = cipher.update(b"{}".format(text))
    encrypted_text += cipher.final()
    return base64.b64encode(encrypted_text)


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


def reindent(text, num_spaces):
    text = [(num_spaces * " ") + line.lstrip() for line in text.splitlines()]
    text = "\n".join(text)
    return text


def generate_base64_contents(text, num_spaces):
    text = text.encode("base64").strip()
    if num_spaces:
        text = reindent(text, 1)
    return text


def generate_base64_from_file(filename, num_spaces):
    text = ""
    with open(filename) as fd:
        text = fd.read()
    return generate_base64_contents(text, num_spaces)


def get_sys_random_chars(size=12, chars=_DEFAULT_CHARS):
    """Generates random characters based on OS.
    """
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def join_quad_str(x):
    return ".".join([get_quad() for _ in xrange(x)])


def safe_inum_str(x):
    return x.replace("@", "").replace("!", "").replace(".", "")


def generate_config(admin_pw, domain, org_name):
    # cfg = dict.fromkeys([
    #     "oxauth_config_base64",
    #     "oxauth_static_conf_base64",
    #     "oxauth_openid_key_base64",  # contents of oxauth-keys.json
    #     "oxauth_error_base64",
    #     "oxtrust_config_base64",
    #     "oxtrust_cache_refresh_base64",
    #     "oxtrust_import_person_base64",
    #     "oxidp_config_base64",
    #     "oxcas_config_base64",
    #     "oxasimba_config_base64",
    #     "scim_rs_client_base64_jwks",
    #     "scim_rp_client_base64_jwks",
    #     "passport_rs_client_base64_jwks",
    #     "passport_rp_client_base64_jwks",
    #     "passport_rp_client_cert_alias", # MUST get 'kid' of passport RP JWKS
    # ], "")

    oxauth_pw = get_random_chars()

    cfg = {}
    cfg["encoded_salt"] = get_random_chars(24)
    cfg["encoded_ldap_pw"] = ldap_encode(admin_pw)
    cfg["encoded_ox_ldap_pw"] = encrypt_text(admin_pw, cfg["encoded_salt"])

    cfg["orgName"] = org_name
    cfg["hostname"] = domain
    cfg["ldap_hostname"] = "N/A"
    cfg["ldapPassFn"] = "N/A"

    cfg["ldap_port"] = 1389
    cfg["ldap_admin_port"] = 4444
    cfg["ldap_jmx_port"] = 1689
    cfg["ldap_binddn"] = cfg["opendj_ldap_binddn"] = "cn=directory manager"
    cfg["ldaps_port"] = 1636
    cfg["ldap_backend_type"] = "je"

    cfg["jetty_base"] = "/opt/gluu/jetty"

    cfg["baseInum"] = "@!{}".format(join_quad_str(4))
    cfg["inumOrg"] = "{}!0001!{}".format(
        cfg["baseInum"],
        join_quad_str(2),
    )
    cfg["inumOrgFN"] = safe_inum_str(cfg["inumOrg"])
    cfg["inumAppliance"] = "{}!0002!{}".format(
        cfg["baseInum"],
        join_quad_str(2),
    )
    cfg["inumApplianceFN"] = safe_inum_str(cfg["inumAppliance"])

    cfg["oxauth_client_id"] = "{}!0008!{}".format(
        cfg["inumOrg"],
        join_quad_str(2),
    )
    cfg["oxauthClient_encoded_pw"] = encrypt_text(
        oxauth_pw,
        cfg["encoded_salt"],
    )
    cfg["scim_rs_client_id"] = "{}!0008!{}".format(
        cfg["inumOrg"],
        join_quad_str(2),
    )
    cfg["scim_rp_client_id"] = "{}!0008!{}".format(
        cfg["inumOrg"],
        join_quad_str(2),
    )
    cfg["passport_rs_client_id"] = "{}!0008!{}".format(
        cfg["inumOrg"],
        join_quad_str(2),
    )
    cfg["passport_rp_client_id"] = "{}!0008!{}".format(
        cfg["inumOrg"],
        join_quad_str(2),
    )
    cfg["passport_rp_client_cert_fn"] = "/etc/certs/passport-rp.pem"
    cfg["passport_rp_client_cert_alg"] = "RS512"
    return cfg


def main(admin_pw="admin", domain="gluu.example.com", org_name="Gluu",
         kv_host="localhost", kv_port=8500):
    from pprint import pprint
    cfg = generate_config(admin_pw, domain, org_name)
    pprint(cfg)

    consul = consulate.Consul(host=kv_host, port=kv_port)

    for k, v in cfg.iteritems():
        # if k in consul.kv:
        #     click.echo("{!r} config already exists ... skipping".format(k))
        #     continue

        click.echo("setting {!r} config".format(k))
        consul.kv.set(k, v)


@click.command()
@click.option("--admin-pw", default="admin",
              help="Password for admin access (default to admin).")
@click.option("--domain", default="gluu.example.com",
              help="Domain for Gluu Server (default to gluu.example.com).")
@click.option("--org-name", default="Gluu",
              help="Organization name (default to Gluu).")
@click.option("--kv-host", default="localhost",
              help="Hostname/IP address of KV store (default to localhost).")
@click.option("--kv-port", default=8500,
              help="Port of KV store (default to 8500).")
def cli(admin_pw, domain, org_name, kv_host, kv_port):
    main(admin_pw, domain, org_name, kv_host, kv_port)


if __name__ == "__main__":
    cli()
