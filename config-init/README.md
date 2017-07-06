# Config Init

A docker image to generate config required by other docker images used in Gluu Server cluster setup.

## Installation

Build the image:

```
docker build --rm --force-rm -t gluufederation/config-init:latest .
```

Or get it from Docker Hub:

```
docker pull gluufederation/config-init:latest
```

## Running The Container

To run this container and see available options, type the following command:

```
docker run --rm gluufederation/config-init
```

The output would be:

```
Usage: entrypoint.py [OPTIONS]

Options:
  --admin-pw TEXT    Password for admin access.  [default: admin]
  --email TEXT       Email for support.  [default: support@gluu.example.com]
  --domain TEXT      Domain for Gluu Server.  [default: gluu.example.com]
  --org-name TEXT    Organization name.  [default: Gluu]
  --kv-host TEXT     Hostname/IP address of KV store.  [default: localhost]
  --kv-port INTEGER  Port of KV store.  [default: 8500]
  --ssl-cert TEXT    Path to SSL certificate.  [default: /etc/certs/gluu_https.crt]
  --ssl-key TEXT     Path to SSL key.  [default: /etc/certs/gluu_https.key]
  --save             Save config to KV store.
  --view             Show generated config.
  --help             Show this message and exit.
```

Note: all options have their default value.

Here's an example to generate config (and save them to Consul KV):

```
docker run --rm \
    -v /path/to/org_ssl.crt:/etc/certs/gluu_https.crt \
    -v /path/to/org_ssl.key:/etc/certs/gluu_https.key \
    gluufederation/config-init \
    --admin-pw my-password \
    --email 'my-email@my.domain.com' \
    --domain my.domain.com \
    --org-name 'My Organization' \
    --kv-host consul.my.domain.com \
    --kv-port 8500 \
    --save \
    --view
```

## FAQ

1.  How to connect to remote Consul KV that bind into private IP address?

    By using SSH tunneling, config-init will be able to connect to the KV.
    For example:

    ```
    ssh -L 8500:<PRIVATE-IP-ADDR>:<CONSUL-CLIENT-PORT> <SSH-USER>@<REMOTE-SERVER>
    ```

    Afterwards, pass `--kv-port 8500` option when running the container:

    ```
    docker run --rm \
        -v /path/to/org_ssl.crt:/etc/certs/gluu_https.crt \
        -v /path/to/org_ssl.key:/etc/certs/gluu_https.key \
        gluufederation/config-init \
        --admin-pw my-password \
        --email 'my-email@my.domain.com' \
        --domain my.domain.com \
        --org-name 'My Organization' \
        --kv-host consul.my.domain.com \
        --kv-port 8500 \
        --save \
        --view
    ```
