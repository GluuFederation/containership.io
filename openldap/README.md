# OpenLDAP

A docker image version of OpenLDAP.

## Installation

Build the image:

```
docker build --rm --force-rm -t gluufederation/openldap:containership .
```

Or get it from Docker Hub:

```
docker pull gluufederation/openldap:containership
```

## Environment Variables

- `GLUU_KV_HOST`: hostname or IP address of Consul.
- `GLUU_KV_PORT`: port of Consul.
- `GLUU_LDAP_HOSTNAME`: hostname of ldap.
- `GLUU_LDAP_INIT_DATA`: whether to import initial LDAPentries (possible value are `true` or `false`).

## Volumes

1. `/opt/gluu/data/main_db` directory
2. `/opt/gluu/data/site_db` directory

## Running The Container

Here's an example to run the container as ldap master with initial LDAP entries:

```
docker run -d \
    --name ldap-master \
    -e GLUU_KV_HOST=my.consul.domain.com \
    -e GLUU_KV_PORT=8500 \
    -e GLUU_LDAP_HOSTNAME=my.ldap.hostname \
    -e GLUU_LDAP_INIT_DATA=true \
    gluufederation/openldap:containership
```

To add other container(s):

```
docker run -d \
    --name ldap-master-no-data \
    -e GLUU_KV_HOST=my.consul.domain.com \
    -e GLUU_KV_PORT=8500 \
    -e GLUU_LDAP_INIT_DATA=false \
    gluufederation/openldap:containership
```

Note: all containers are synchronized using `ntp` pointed to [Google NTP](https://developers.google.com/time/) servers.

## Customizing OpenLDAP

If user has a custome ldap schema then user need to put the schema file in a tar.gz archive.
This archive will just contain schama file. User need to provide a url for that archive file.
user must pass custom schema to init ldap master to take effect.

Here's an example to run the container as ldap master with initial LDAP entries and custom schema:

```
docker run -d \
    --name ldap-master \
    -e GLUU_KV_HOST=my.consul.domain.com \
    -e GLUU_KV_PORT=8500 \
    -e GLUU_LDAP_HOSTNAME=my.ldap.hostname \
    -e GLUU_LDAP_INIT_DATA=true \
    -e GLUU_CUSTOM_SCHEMA_URL=<https://url/of/custom-schema.tar.gz>
    gluufederation/openldap:containership
```
