# openldap

A docker image version of openldap.

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
- `GLUU_LDAP_HOSTNAME`: host name of ldap.

## Volumes

1. `/opt/gluu/data/main_db` directory
2. `/opt/gluu/data/site_db` directory

## Running The Container

Here's an example to run the container:

```
docker run -d \
    --name ldap \
    -e GLUU_KV_HOST=my.consul.domain.com \
    -e GLUU_KV_PORT=8500 \
    -e GLUU_LDAP_HOSTNAME=my.ldap.hostname \
    gluufederation/openldap:containership
```

## Customizing openldap

TODO
