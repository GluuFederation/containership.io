import os

import consulate


GLUU_DOMAIN = os.environ.get("GLUU_DOMAIN", "localhost")
GLUU_OXAUTH_BACKEND = os.environ.get("GLUU_OXAUTH_BACKEND", "localhost:8081")
GLUU_OXTRUST_BACKEND = os.environ.get("GLUU_OXTRUST_BACKEND", "localhost:8082")
GLUU_KV_HOST = os.environ.get("GLUU_KV_HOST", "localhost")
GLUU_KV_PORT = os.environ.get("GLUU_KV_PORT", 8500)

consul = consulate.Consul(host=GLUU_KV_HOST, port=GLUU_KV_PORT)


def render_ssl_cert():
    ssl_cert = consul.kv.get("ssl_cert")
    if ssl_cert:
        with open("/etc/certs/gluu_https.crt", "w") as fd:
            fd.write(ssl_cert)


def render_ssl_key():
    ssl_key = consul.kv.get("ssl_key")
    if ssl_key:
        with open("/etc/certs/gluu_https.key", "w") as fd:
            fd.write(ssl_key)


def render_nginx_conf():
    txt = ""
    with open("/opt/templates/gluu_https.conf.tmpl") as fd:
        txt = fd.read()

    if txt:
        with open("/etc/nginx/sites-available/gluu_https.conf", "w") as fd:
            rendered_txt = txt % {
                "gluu_domain": GLUU_DOMAIN,
                "gluu_oxauth_backend": GLUU_OXAUTH_BACKEND,
                "gluu_oxtrust_backend": GLUU_OXTRUST_BACKEND,
            }
            fd.write(rendered_txt)

        if not os.path.exists("/etc/nginx/sites-enabled/gluu_https.conf"):
            os.symlink("/etc/nginx/sites-available/gluu_https.conf",
                       "/etc/nginx/sites-enabled/gluu_https.conf")
            os.unlink("/etc/nginx/sites-enabled/default")


if __name__ == "__main__":
    render_ssl_cert()
    render_ssl_key()
    render_nginx_conf()
