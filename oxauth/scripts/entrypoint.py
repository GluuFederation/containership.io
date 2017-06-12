import os

import consulate

GLUU_LDAP_URL = os.environ.get("GLUU_LDAP_URL", "localhost:1636")
GLUU_KV_HOST = os.environ.get("GLUU_KV_HOST", "localhost")
GLUU_KV_PORT = os.environ.get("GLUU_KV_PORT", 8500)

consul = consulate.Consul(host=GLUU_KV_HOST, port=GLUU_KV_PORT)


def render_salt():
    encode_salt = consul.kv.get("encoded_salt")

    with open("/opt/templates/salt.tmpl") as fr:
        txt = fr.read()
        with open("/etc/gluu/conf/salt", "w") as fw:
            rendered_txt = txt % {"encode_salt": encode_salt}
            fw.write(rendered_txt)


def render_ldap_properties():
    ldap_binddn = consul.kv.get("ldap_binddn")
    encoded_ox_ldap_pw = consul.kv.get("encoded_ox_ldap_pw")
    inumAppliance = consul.kv.get("inumAppliance")
    use_ssl = consul.kv.get("ldap_use_ssl", "false")

    with open("/opt/templates/ox-ldap.properties.tmpl") as fr:
        txt = fr.read()

        with open("/etc/gluu/conf/ox-ldap.properties", "w") as fw:
            rendered_txt = txt % {
                "ldap_binddn": ldap_binddn,
                "encoded_ox_ldap_pw": encoded_ox_ldap_pw,
                "inumAppliance": inumAppliance,
                "ldap_url": GLUU_LDAP_URL,
                "use_ssl": use_ssl,
            }
            fw.write(rendered_txt)


if __name__ == "__main__":
    render_salt()
    render_ldap_properties()
