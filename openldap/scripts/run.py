import os
import re
import subprocess

import consulate


GLUU_DATASTORE = os.environ.get('GLUU_DATASTORE', 'localhost')
GLUU_DATASTORE_PORT = os.environ.get('GLUU_DATASTORE_PORT', 8500)
#TODO env var acesslog_comentout

consul = consulate.Consul(host=GLUU_DATASTORE, port=GLUU_DATASTORE_PORT)

#functions taken from setup.py
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

# def run(args, cwd=None, env=None, useWait=False):
#     try:
#         p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=env)
#         if useWait:
#             code = p.wait()
#             self.logIt('Run: %s with result code: %d' % (' '.join(args), code) )
#         else:
#             output, err = p.communicate()
#             if output:
#                 self.logIt(output)
#             if err:
#                 self.logIt(err, True)
#     except:
#         self.logIt("Error running command : %s" % " ".join(args), True)
#         self.logIt(traceback.format_exc(), True)

#functions taken from setup.py

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


# def import_ldif_openldap():
#     ldif_files = [ ldif_base,
#                    ldif_appliance,
#                    ldif_attributes,
#                    ldif_scopes,
#                    ldif_clients,
#                    ldif_people,
#                    ldif_groups,
#                    ldif_site,
#                    ldif_scripts,
#                    ldif_configuration,
#                    ldif_scim,
#                    ldif_asimba,
#                    ldif_passport,
#                    ldif_passport_config,
#                    ldif_idp
#                 ]

#     cmd = '/opt/symas/bin/slapadd'
#     config = '/opt/symas/etc/openldap/slapd.conf'
#     realInstallDir = os.path.realpath(install_dir)
#     for ldif in ldif_files:
#         if 'site.ldif' in ldif:
#             run(['/bin/su', 'ldap', '-c', "cd " + realInstallDir + "; " + " ".join([cmd, '-b', 'o=site', '-f', config, '-l', ldif])])
#         else:
#             run(['/bin/su', 'ldap', '-c', "cd " + realInstallDir + "; " + " ".join([cmd, '-b', 'o=gluu', '-f', config, '-l', ldif])])


def run():
    configure_openldap()
    #import_ldif_openldap()

if __name__ == '__main__':
    run()


# related setup functions,
# start_services
# install_ldap_server 
# install_openldap (done in dockerfile)
# configure_openldap
# import_ldif_openldap