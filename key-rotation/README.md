# KeyRotation

A docker image to rotate oxAuth keys.

## Installation

Build the image:

```
docker build --rm --force-rm -t gluufederation/key-rotation:containership .
```

Or get it from Docker Hub:

```
docker pull gluufederation/key-rotation:containership
```

## Environment Variables

- `GLUU_KV_HOST`: hostname or IP address of Consul.
- `GLUU_KV_PORT`: port of Consul.
- `GLUU_LDAP_URL`: URL to LDAP (single instance or load-balanced).

## Running The Container

Here's an example to run the container as ldap master with initial LDAP entries:

```
docker run -d \
    --name ldap-master \
    -e GLUU_KV_HOST=my.consul.domain.com \
    -e GLUU_KV_PORT=8500 \
    -e GLUU_LDAP_URL=my.ldap.domain.com:1636 \
    -e GLUU_KEY_ROTATION_INTERVAL=2 \
    gluufederation/key-rotation:containership
```

## TODO

1. Distribute `oxauth-keys.jks`
