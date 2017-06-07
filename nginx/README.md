# nginx

A docker image version of nginx.

## Installation

Build the image:

```
docker build --rm --force-rm -t gluufederation/nginx:containership .
```

## Running The Container

Here's an example to run the container:

```
docker run -d \
    --name nginx \
    -e GLUU_KV_HOST=my.consul.domain.com \
    -e GLUU_KV_PORT=8500 \
    -e GLUU_OXAUTH_BACKEND=my.oxauth.domain.com:8081 \
    -e GLUU_OXTRUST_BACKEND=my.oxtrust.domain.com:8082 \
    gluufederation/nginx:containership
```
