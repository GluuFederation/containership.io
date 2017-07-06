FROM ubuntu:14.04

MAINTAINER Gluu Inc. <support@gluu.org>

# Ubuntu packages
RUN echo 'deb http://ppa.launchpad.net/nginx/stable/ubuntu trusty main' >> /etc/apt/sources.list.d/nginx.list \
    && echo 'deb-src http://ppa.launchpad.net/nginx/stable/ubuntu trusty main ' >> /etc/apt/sources.list.d/nginx.list \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys C300EE8C

RUN apt-get update \
    && apt-get install -y nginx openssl python python-pip wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# =====
# nginx
# =====

RUN mkdir -p /etc/certs

RUN openssl dhparam -out /etc/certs/dhparams.pem 2048

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# Ports for nginx
EXPOSE 80
EXPOSE 443

# ====
# tini
# ====

ENV TINI_VERSION v0.15.0
RUN wget -q https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini -O /tini \
    && chmod +x /tini
ENTRYPOINT ["/tini", "--"]

# ====
# gosu
# ====

ENV GOSU_VERSION 1.10
RUN wget -q https://github.com/tianon/gosu/releases/download/${GOSU_VERSION}/gosu-amd64 -O /usr/local/bin/gosu \
    && chmod +x /usr/local/bin/gosu

# ======
# Python
# ======

# Python packages
RUN pip install -U pip

# A workaround to address https://github.com/docker/docker-py/issues/1054
# and to make sure latest pip is being used, not from OS one
ENV PYTHONPATH="/usr/local/lib/python2.7/dist-packages:/usr/lib/python2.7/dist-packages"

RUN pip install "consulate==0.6.0"

# ==========
# misc stuff
# ==========

LABEL vendor="Gluu Federation"

ENV GLUU_OXAUTH_BACKEND localhost:8081
ENV GLUU_OXTRUST_BACKEND localhost:8082
ENV GLUU_KV_HOST localhost
ENV GLUU_KV_PORT 8500

RUN mkdir -p /opt/scripts /opt/templates

COPY templates /opt/templates/
COPY scripts /opt/scripts/

RUN chmod +x /opt/scripts/entrypoint.sh
CMD ["/opt/scripts/entrypoint.sh"]
