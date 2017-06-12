import os
import re
import subprocess
import glob
import tempfile
import shutil

import consulate


GLUU_DATASTORE = os.environ.get('GLUU_DATASTORE', 'localhost')
GLUU_DATASTORE_PORT = os.environ.get('GLUU_DATASTORE_PORT', 8500)
#TODO env var acesslog_comentout
TMPDIR = tempfile.mkdtemp()


consul = consulate.Consul(host=GLUU_DATASTORE, port=GLUU_DATASTORE_PORT)


#START functions taken from setup.py
def fomatWithDict(text, dictionary):
    text = re.sub(r"%([^\(])", r"%%\1", text)
    text = re.sub(r"%$", r"%%", text)  # There was a % at the end?
    return text % dictionary

def commentOutText(text):
    textLines = text.split('\n')
    lines = []
    for textLine in textLines:
        lines.append('#%s' % textLine)
    return "\n".join(lines)

def run(args, cwd=None, env=None, useWait=False):
    try:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=env)
        if useWait:
            code = p.wait()
            print 'Run: %s with result code: %d' % (' '.join(args), code)
        else:
            output, err = p.communicate()
            if output:
                print output
            if err:
                print err
    except:
        print "Error running command : %s" % " ".join(args)
        print traceback.format_exc()
#END functions taken from setup.py


def configure_openldap():
    src = '/ldap/templates/slapd.conf'
    dest = '/opt/symas/etc/openldap/slapd.conf'
    accesslog_file = '/ldap/static/accesslog.conf'
    gluu_accesslog_file = '/ldap/static/o_gluu_accesslog.conf'

    with open(src, 'r') as fp:
        slapd_template = fp.read()

    with open(accesslog_file, 'r') as fp:
        access_log_text = fp.read()

    with open(gluu_accesslog_file, 'r') as fp:
        gluu_accesslog_text = fp.read()

    ctx_data  = {
    'openldapSchemaFolder' : '/opt/gluu/schema/openldap',
    'openldapTLSCACert': '',
    'openldapTLSCert': '',
    'openldapTLSKey' : '',
    'encoded_ldap_pw' : consul.kv.get('encoded_ldap_pw'),
    'openldap_accesslog_conf' : commentOutText(access_log_text),
    'openldap_gluu_accesslog' : commentOutText(gluu_accesslog_text),
    }

    with open(dest, 'w') as fp:
        fp.write(fomatWithDict(slapd_template, ctx_data))


def render_ldif():
    # TODO: check ctx data and update accordingly with consul KV
    ctx_data = {
            "oxauth_client_id": consul.kv.get(''),
            "oxauth_client_encoded_pw": consul.kv.get(''),
            "encoded_ldap_pw": consul.kv.get(''),
            "encoded_ox_ldap_pw": consul.kv.get(''),
            "inum_appliance": consul.kv.get(''),
            "hostname": consul.kv.get(''), #self.ldap_failover_hostname() TODO
            "ox_cluster_hostname": consul.kv.get(''),
            "ldaps_port": consul.kv.get(''),
            "ldap_binddn": consul.kv.get(''),
            "inum_org": consul.kv.get(''),
            "inum_org_fn": consul.kv.get(''),
            "org_name": consul.kv.get(''),
            "scim_rp_client_id": consul.kv.get(''),
        }

    ldif_template_base = '/ldap/templates/ldif'
    pattern = '/*.ldif'
    for file_path in glob.glob(ldif_template_base+pattern):
        with open(file_path, 'r') as fp:
            template = fp.read()
        #render
        rendered_content = template % ctx_data
        # write to tmpdir
        with open(os.path.join(TMPDIR, os.path.basename(file_path)), 'w') as fp:
            fp.write(rendered_content)


def import_ldif():
    slapadd_cmd = '/opt/symas/bin/slapadd'
    pattern = '/*.ldif'
    config = '/opt/symas/etc/openldap/slapd.conf'
    for ldif_file_path in glob.glob(TMPDIR+pattern):
        if 'site.ldif' in ldif_file_path:
            run([" ".join([slapadd_cmd, '-b', 'o=site', '-f', config, '-l', ldif_file_path])])
        else:
            run([" ".join([slapadd_cmd, '-b', 'o=gluu', '-f', config, '-l', ldif_file_path])])


def cleanup():
    shutil.rmtree(TMPDIR)


def run():
    configure_openldap()
    render_ldif()
    import_ldif()
    cleanup()


if __name__ == '__main__':
    run()


# related setup functions,
# start_services
# install_ldap_server 
# install_openldap (done in dockerfile)
# configure_openldap
# import_ldif_openldap