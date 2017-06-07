FROM ubuntu:14.04

MAINTAINER Shouro <shouro@gluu.org>


RUN groupadd -r ldap && useradd -r -g ldap ldap


RUN apt-get update && apt-get install -y \
    openjdk-7-jre-headless \
    unzip \
    wget \
    curl \
    python \
    python-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# ENV variables
ENV OPENDJ_VERSION 3.0.0.gluu-SNAPSHOT
ENV OPENDJ_DOWNLOAD_URL http://ox.gluu.org/maven/org/forgerock/opendj/opendj-server-legacy/${OPENDJ_VERSION}/opendj-server-legacy-${OPENDJ_VERSION}.zip


# Unzip opendj
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


# Install gosu
RUN curl -o /usr/local/bin/gosu -SL 'https://github.com/tianon/gosu/releases/download/1.10/gosu-amd64' && chmod +x /usr/local/bin/gosu


# Update pip
RUN pip install -U pip


# A workaround to address https://github.com/docker/docker-py/issues/1054
# and to make sure latest pip is being used, not from OS one
ENV PYTHONPATH="/usr/local/lib/python2.7/dist-packages:/usr/lib/python2.7/dist-packages"


WORKDIR /gluu


# Copy script
COPY script ./script/


# Install requirements
RUN pip install --no-cache-dir -r ./script/requirements.txt


#-----------------------------------------------------------------------------------------
# Directory for certificates
RUN mkdir -p /etc/certs


# Static
COPY static ./data/static/

# Templates
COPY templates ./data/templates/


# Schema
#RUN mkdir -p /opt/opendj/template/config/schema
#RUN mkdir -p /opt/opendj/ldif
#COPY schema/101-ox.ldif /opt/opendj/template/config/schema
#COPY schema/77-customAttributes.ldif /opt/opendj/template/config/schema
#COPY schema/96-eduperson.ldif /opt/opendj/template/config/schema
#COPY o_site.ldif /opt/opendj/ldif
#-----------------------------------------------------------------------------------------


# LDAP port
EXPOSE 1389
# LDAPS port
EXPOSE 1636
# Admin port
EXPOSE 4444
# replication port
EXPOSE 8989


# Entrypoint
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]





