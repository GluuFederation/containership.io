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
- `GLUU_LDAP_HOSTNAME`: hostname of ldap (only useful in provider role).
- `GLUU_LDAP_REPLICATE_FROM`: location of ldap provider (only useful in consumer role).

## Volumes

1. `/opt/gluu/data/main_db` directory
2. `/opt/gluu/data/site_db` directory

## Running The Container

Here's an example to run the container as ldap provider:

```
docker run -d \
    --name ldap-provider \
    -e GLUU_KV_HOST=my.consul.domain.com \
    -e GLUU_KV_PORT=8500 \
    -e GLUU_LDAP_HOSTNAME=my.ldap.hostname \
    gluufederation/openldap:containership
```

Here's an example to run the container as ldap consumer:

```
docker run -d \
    --name ldap-consumer \
    -e GLUU_KV_HOST=my.consul.domain.com \
    -e GLUU_KV_PORT=8500 \
    -e GLUU_LDAP_REPLICATE_FROM=ldap-provider.domain.com:1389 \
    gluufederation/openldap:containership
```

## Customizing openldap

TODO
