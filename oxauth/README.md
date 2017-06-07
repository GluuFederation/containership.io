# oxAuth

A docker image version of oxAuth.

## Installation

Build the image:

```
docker build --rm --force-rm -t gluufederation/oxauth:containership .
```

## Environment Variables

- `GLUU_KV_HOST`: hostname or IP address of Consul.
- `GLUU_KV_PORT`: port of Consul.
- `GLUU_LDAP_URL`: URL to LDAP (single instance or load-balanced).
- `GLUU_CUSTOM_OXTRUST_URL`: URL to custom oxTrust files packed using `.tar.gz` format.

## Running The Container

Here's an example to run the container:

```
docker run -d \
    --name oxauth \
    -e GLUU_KV_HOST=my.consul.domain.com \
    -e GLUU_KV_PORT=8500 \
    -e GLUU_LDAP_URL=my.ldap.domain.com:1636 \
    -e GLUU_CUSTOM_OXAUTH_URL=url-to-custom-oxauth.tar.gz \
    gluufederation/oxauth:containership
```
