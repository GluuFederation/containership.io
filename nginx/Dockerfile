FROM ubuntu:14.04

MAINTAINER Isman <isman@gluu.org>

RUN echo 'deb http://ppa.launchpad.net/nginx/stable/ubuntu trusty main' >> /etc/apt/sources.list.d/nginx.list \
    && echo 'deb-src http://ppa.launchpad.net/nginx/stable/ubuntu trusty main ' >> /etc/apt/sources.list.d/nginx.list \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys C300EE8C

RUN apt-get update \
    && apt-get install -y nginx openssl python \
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

LABEL vendor="Gluu Federation"

# Ports for nginx
EXPOSE 80
EXPOSE 443

# ENV for containership.io
ENV GLUU_DOMAIN localhost
ENV GLUU_OXAUTH_BACKEND localhost:8081
ENV GLUU_OXTRUST_BACKEND localhost:8082

COPY scripts/entrypoint.sh /opt/scripts/
COPY scripts/entrypoint.py /opt/scripts/
RUN chmod +x /opt/scripts/entrypoint.sh
ENTRYPOINT ["/opt/scripts/entrypoint.sh"]
