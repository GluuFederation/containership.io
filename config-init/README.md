# Config Init

A docker image to generate config required by other docker images used in Gluu Server cluster setup.

## Installation

Build the image:

```
docker build --rm --force-rm -t gluufederation/config-init .
```

Or get it from Docker Hub:

```
docker pull gluufederation/config-init
```

## Running The Container

Prerequisites:

- Make sure docker daemon is running.
- Make sure Consul container is running.

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
  --help             Show this message and exit.
```

Note: all options have their default value.

Here's an example to generate config (and save them to Consul KV):

```
docker run --rm gluufederation/config-init \
    --admin-pw my-password \
    --email 'my-email@my.domain.com' \
    --domain my.domain.com \
    --org-name 'My Organization' \
    --kv-host consul.my.domain.com \
    --kv-port 8500
```
