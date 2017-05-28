FROM gluufederation/base

MAINTAINER Shouro <shouro@gluu.org>

RUN groupadd -r ldap && useradd -r -g ldap ldap

RUN apt-get update && apt-get install -y \
    openjdk-7-jre-headless \
    unzip \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ENV variables
ENV OPENDJ_VERSION 3.0.0.gluu-SNAPSHOT
ENV OPENDJ_DOWNLOAD_URL http://ox.gluu.org/maven/org/forgerock/opendj/opendj-server-legacy/${OPENDJ_VERSION}/opendj-server-legacy-${OPENDJ_VERSION}.zip

RUN wget -q "$OPENDJ_DOWNLOAD_URL" -P /tmp \
    && unzip -qq /tmp/opendj-server-legacy-${OPENDJ_VERSION}.zip -d /opt \
    && rm -f /tmp/opendj-server-legacy-${OPENDJ_VERSION}.zip

# the LABEL defined before downloading ox war/jar files to make sure
# it gets the latest build for specific version
LABEL vendor="Gluu Federation" \
      org.gluu.gluu-opendj.version="3.0.0-gluu" \
      org.gluu.gluu-opendj.build-date="2016-04-11"

# JAR files required to generate OpenID Connect keys
#RUN mkdir -p /opt/gluu/lib
#wget -q http://ox.gluu.org/maven/org/xdi/oxauth-client/3.1.0-SNAPSHOT/oxauth-client-3.1.0-SNAPSHOT-jar-with-dependencies.jar -O /opt/gluu/lib/keygen.jar

# Directory for certificates
#RUN mkdir -p /etc/certs

#RUN mkdir -p /opt/opendj/template/config/schema
#RUN mkdir -p /opt/opendj/ldif

# Copy static templates
#COPY opendj_index.json /opt/opendj
#COPY o_site.ldif /opt/opendj/ldif
#COPY 101-ox.ldif /opt/opendj/template/config/schema
#COPY 77-customAttributes.ldif /opt/opendj/template/config/schema
#COPY 96-eduperson.ldif /opt/opendj/template/config/schema

# LDAP port
EXPOSE 1389

# LDAPS port
EXPOSE 1636

# replication port
EXPOSE 8989
