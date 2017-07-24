# oxAuth

A docker image version of oxAuth.

## Installation

Build the image:

```
docker build --rm --force-rm -t gluufederation/oxauth:latest .
```

Or get it from Docker Hub:

```
docker pull gluufederation/oxauth:latest
```

## Environment Variables

- `GLUU_KV_HOST`: hostname or IP address of Consul.
- `GLUU_KV_PORT`: port of Consul.
- `GLUU_LDAP_URL`: URL to LDAP (single instance or load-balanced).
- `GLUU_CUSTOM_OXAUTH_URL`: URL to downloadable custom oxAuth files packed using `.tar.gz` format.

## Volumes

1. `/opt/gluu/jetty/oxauth/custom/pages` directory
2. `/opt/gluu/jetty/oxauth/custom/static` directory
3. `/opt/gluu/jetty/oxauth/lib/ext` directory

## Running The Container

Here's an example to run the container:

```
docker run -d \
    --name oxauth \
    -e GLUU_KV_HOST=my.consul.domain.com \
    -e GLUU_KV_PORT=8500 \
    -e GLUU_LDAP_URL=my.ldap.domain.com:1636 \
    -e GLUU_CUSTOM_OXAUTH_URL=http://my.domain.com/resources/custom-oxauth.tar.gz \
    gluufederation/oxauth:containership
```

## Customizing oxAuth

oxAuth can be customized by providing HTML pages, static resource files (i.e. CSS), or JAR libraries.
Refer to https://gluu.org/docs/ce/3.0.1/operation/custom-loginpage/ for an example on how to customize oxAuth.

There are 2 ways to run oxAuth with custom files:

1.  Pass `GLUU_CUSTOM_OXAUTH_URL` environment variable; the container will download and extract the file into
    appropriate location before running the application.

    ```
    docker run -d \
        --name oxauth \
        -e GLUU_KV_HOST=my.consul.domain.com \
        -e GLUU_KV_PORT=8500 \
        -e GLUU_LDAP_URL=my.ldap.domain.com:1636 \
        -e GLUU_CUSTOM_OXAUTH_URL=http://my.domain.com/resources/custom-oxauth.tar.gz \
        gluufederation/oxauth:containership
    ```

    The `.tar.gz` file must consist of following directories:

    ```
    ├── lib
    │   └── ext
    ├── pages
    └── static
    ```

2.  Map volumes from host to container.

    ```
    docker run -d \
        --name oxauth \
        -e GLUU_KV_HOST=my.consul.domain.com \
        -e GLUU_KV_PORT=8500 \
        -e GLUU_LDAP_URL=my.ldap.domain.com:1636 \
        -v /path/to/custom/pages:/opt/gluu/jetty/oxauth/custom/pages \
        -v /path/to/custom/static:/opt/gluu/jetty/oxauth/custom/static \
        -v /path/to/custom/lib/ext:/opt/gluu/jetty/oxauth/lib/ext \
        gluufederation/oxauth:containership
    ```
