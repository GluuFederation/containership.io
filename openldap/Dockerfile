FROM ubuntu:14.04

MAINTAINER Shouro <shouro@gluu.org>

#RUN groupadd -r ldap && useradd -r -g ldap ldap

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    python \
    python-dev \
    python-pip \
    swig \
    libssl-dev \
    ntp \
    libldap2-dev \
    libsasl2-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install gosu
RUN curl -o /usr/local/bin/gosu -SL 'https://github.com/tianon/gosu/releases/download/1.10/gosu-amd64' && chmod +x /usr/local/bin/gosu

# update pip
RUN pip install -U pip

# A workaround to address https://github.com/docker/docker-py/issues/1054
# and to make sure latest pip is being used, not from OS one
ENV PYTHONPATH="/usr/local/lib/python2.7/dist-packages:/usr/lib/python2.7/dist-packages"

#install_openldap
ENV OPENLDAP_DEB_URL https://repo.gluu.org/ubuntu/symas-openldap-gluu.amd64_2.4.44-20161020_amd64.deb

RUN wget -q ${OPENLDAP_DEB_URL} -O /tmp/openldap.deb \
    && dpkg --install /tmp/openldap.deb \
    && rm -rf /tmp/openldap.deb

RUN mkdir -p /var/symas/run
#RUN chmod -R 775 /var/symas/run
#RUN chgrp -R ldap /var/symas/run

# Add Tini
ENV TINI_VERSION v0.15.0
RUN wget -q https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini -O /tini \
    && chmod +x /tini
ENTRYPOINT ["/tini", "--"]

WORKDIR /ldap

COPY requirements.txt ./

# Install requirements
RUN pip install --no-cache-dir -r ./requirements.txt

#configure_openldap
RUN mkdir -p /opt/symas/etc/openldap
RUN mkdir -p /opt/gluu/schema/openldap
RUN mkdir -p /opt/gluu/data/accesslog
RUN mkdir -p /etc/certs
RUN mkdir -p /opt/symas/etc/openldap/slapd.d

COPY schema /opt/gluu/schema/openldap
COPY templates ./templates
COPY scripts ./scripts
COPY static ./static
RUN cp ./templates/slapd/symas-openldap.conf /opt/symas/etc/openldap/symas-openldap.conf
RUN cp ./static/ntp.conf /etc/

# Data dir
RUN mkdir -p /opt/gluu/data/main_db
RUN mkdir -p /opt/gluu/data/site_db

# Volumes
VOLUME /opt/gluu/data/main_db
VOLUME /opt/gluu/data/site_db

RUN touch /var/log/replicator.log
RUN chmod +x ./scripts/replicator.sh

# Custom schema path
RUN mkdir -p /ldap/custom_schema

#EXPOSE 1636
EXPOSE 1389

# Entrypoint
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
