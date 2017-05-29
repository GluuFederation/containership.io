import os

GLUU_DOMAIN = os.environ.get("GLUU_DOMAIN", "localhost")
GLUU_OXAUTH_BACKEND = os.environ.get("GLUU_OXAUTH_BACKEND", "localhost:8081")
GLUU_OXTRUST_BACKEND = os.environ.get("GLUU_OXTRUST_BACKEND", "localhost:8082")


def render_ssl_cert():
    pass


def render_ssl_key():
    pass


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


if __name__ == "__main__":
    render_ssl_cert()
    render_ssl_key()
    render_nginx_conf()
