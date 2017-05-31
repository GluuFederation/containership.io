FROM ubuntu:14.04

MAINTAINER Isman <isman@gluu.org>

# Ubuntu packages
RUN echo 'deb http://ppa.launchpad.net/nginx/stable/ubuntu trusty main' >> /etc/apt/sources.list.d/nginx.list \
    && echo 'deb-src http://ppa.launchpad.net/nginx/stable/ubuntu trusty main ' >> /etc/apt/sources.list.d/nginx.list \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys C300EE8C

RUN apt-get update \
    && apt-get install -y nginx openssl python python-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Directory for certificates
RUN mkdir -p /etc/certs

# Directory for scripts
RUN mkdir -p /opt/scripts/

# Directory for templates
RUN mkdir -p /opt/templates/

RUN openssl dhparam -out /etc/certs/dhparams.pem 2048

COPY templates/gluu_https.conf.tmpl /opt/templates/

# Python packages
RUN pip install -U pip

# A workaround to address https://github.com/docker/docker-py/issues/1054
# and to make sure latest pip is being used, not from OS one
ENV PYTHONPATH="/usr/local/lib/python2.7/dist-packages:/usr/lib/python2.7/dist-packages"

RUN pip install consulate

LABEL vendor="Gluu Federation"

# Ports for nginx
EXPOSE 80
EXPOSE 443

# Gluu Server domain, e.g. my.cluster.com
ENV GLUU_DOMAIN localhost

# oxAuth backend URL, e.g. my.cluster.com:8081
ENV GLUU_OXAUTH_BACKEND localhost:8081

# oxTrust backend URL, e.g. my.cluster.com:8081
ENV GLUU_OXTRUST_BACKEND localhost:8082

# KV store hostname or IP address
ENV GLUU_KV_HOST localhost

# KV store port
ENV GLUU_KV_PORT 8500

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

COPY scripts/entrypoint.sh /opt/scripts/
COPY scripts/entrypoint.py /opt/scripts/
RUN chmod +x /opt/scripts/entrypoint.sh
ENTRYPOINT ["/opt/scripts/entrypoint.sh"]
