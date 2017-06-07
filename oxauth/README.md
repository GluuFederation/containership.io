# oxAuth

A docker image version of oxAuth.

## Installation

Build the image:

```
docker build --rm --force-rm -t gluufederation/oxauth:containership .
```

## Running The Container

Here's an example to run the container:

```
docker run -d \
    --name oxauth \
    -e GLUU_KV_HOST=my.consul.domain.com \
    -e GLUU_KV_PORT=8500 \
    -e GLUU_LDAP_URL=my.ldap.domain.com:1636 \
    gluufederation/oxauth:containership
```
