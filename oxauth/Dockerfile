FROM ubuntu:14.04

MAINTAINER Shouro <shouro@gluu.org>

# ===============
# Ubuntu packages
# ===============

# JDK 8 repo
RUN echo "deb http://ppa.launchpad.net/openjdk-r/ppa/ubuntu trusty main" >> /etc/apt/sources.list.d/openjdk.list \
    && echo "deb-src http://ppa.launchpad.net/openjdk-r/ppa/ubuntu trusty main" >> /etc/apt/sources.list.d/openjdk.list \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 86F44E2A

RUN apt-get update && apt-get install -y \
    openjdk-8-jre-headless \
    unzip \
    wget \
    python \
    python-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# workaround for bug on ubuntu 14.04 with openjdk-8-jre-headless
RUN /var/lib/dpkg/info/ca-certificates-java.postinst configure

# Set openjdk 8 as default java
RUN cd /usr/lib/jvm && ln -s java-1.8.0-openjdk-amd64 default-java

# =====
# Jetty
# =====

ENV JETTY_VERSION 9.3.14.v20161028
ENV JETTY_TGZ_URL https://repo1.maven.org/maven2/org/eclipse/jetty/jetty-distribution/${JETTY_VERSION}/jetty-distribution-${JETTY_VERSION}.tar.gz
ENV JETTY_HOME /opt/jetty
ENV JETTY_BASE /opt/gluu/jetty
ENV JETTY_USER_HOME_LIB /home/jetty/lib

# Install jetty
RUN wget -q ${JETTY_TGZ_URL} -O /tmp/jetty.tar.gz \
    && tar -xzf /tmp/jetty.tar.gz -C /opt \
    && mv /opt/jetty-distribution-${JETTY_VERSION} ${JETTY_HOME} \
    && rm -rf /tmp/jetty.tar.gz

RUN mv ${JETTY_HOME}/etc/webdefault.xml ${JETTY_HOME}/etc/webdefault.xml.bak \
    && mv ${JETTY_HOME}/etc/jetty.xml ${JETTY_HOME}/etc/jetty.xml.bak
COPY jetty/webdefault.xml ${JETTY_HOME}/etc/
COPY jetty/jetty.xml ${JETTY_HOME}/etc/

# Ports required by jetty
EXPOSE 8080

# ======
# Jython
# ======

ENV JYTHON_VERSION 2.7.0
ENV JYTHON_DOWNLOAD_URL http://central.maven.org/maven2/org/python/jython-standalone/${JYTHON_VERSION}/jython-standalone-${JYTHON_VERSION}.jar

# Install Jython
RUN wget -q ${JYTHON_DOWNLOAD_URL} -O /tmp/jython.jar \
    && unzip -q /tmp/jython.jar -d /opt/jython \
    && rm -f /tmp/jython.jar

# ======
# oxAuth
# ======

ENV OX_VERSION 3.0.1
ENV OX_BUILD_DATE 2017-02-24
ENV OXAUTH_DOWNLOAD_URL https://ox.gluu.org/maven/org/xdi/oxauth-server/${OX_VERSION}/oxauth-server-${OX_VERSION}.war

# the LABEL defined before downloading ox war/jar files to make sure
# it gets the latest build for specific version
LABEL vendor="Gluu Federation" \
      org.gluu.oxauth-server.version="${OX_VERSION}" \
      org.gluu.oxauth-server.build-date="${OX_BUILD_DATE}"

# Install oxAuth
RUN wget -q ${OXAUTH_DOWNLOAD_URL} -O /tmp/oxauth.war \
    && mkdir -p ${JETTY_BASE}/oxauth/webapps \
    && unzip -qq /tmp/oxauth.war -d ${JETTY_BASE}/oxauth/webapps/oxauth \
    && java -jar ${JETTY_HOME}/start.jar jetty.home=${JETTY_HOME} jetty.base=${JETTY_BASE}/oxauth --add-to-start=deploy,http,jsp,servlets,ext,http-forwarded \
    && rm -f /tmp/oxauth.war

RUN mkdir -p ${JETTY_USER_HOME_LIB}
RUN wget -q http://central.maven.org/maven2/org/bouncycastle/bcprov-jdk16/1.46/bcprov-jdk16-1.46.jar -O ${JETTY_USER_HOME_LIB}/bcprov-jdk16-1.46.jar

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
RUN pip install -U pip

# A workaround to address https://github.com/docker/docker-py/issues/1054
# and to make sure latest pip is being used, not from OS one
ENV PYTHONPATH="/usr/local/lib/python2.7/dist-packages:/usr/lib/python2.7/dist-packages"

RUN pip install "consulate==0.6.0"

# ====
# cron
# ====

RUN mkdir -p /opt/jks_sync
COPY cron/jks_sync /etc/cron.d/
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/jks_sync
RUN touch /var/log/jks_sync.log

# ==========
# misc stuff
# ==========

RUN mkdir -p /etc/certs \
    && mkdir -p /opt/gluu/python/libs \
    && mkdir -p ${JETTY_BASE}/oxauth/custom/pages ${JETTY_BASE}/oxauth/custom/static \
    && mkdir -p /etc/gluu/conf \
    && mkdir -p /opt/templates

COPY libs /opt/gluu/python/libs
COPY certs /etc/certs
COPY jetty/oxauth_web_resources.xml ${JETTY_BASE}/oxauth/webapps/
COPY conf/ox-ldap.properties.tmpl /opt/templates/
COPY conf/salt.tmpl /opt/templates/

ENV GLUU_LDAP_URL localhost:1636
ENV GLUU_KV_HOST localhost
ENV GLUU_KV_PORT 8500
ENV GLUU_CUSTOM_OXAUTH_URL ""

VOLUME ${JETTY_BASE}/oxauth/custom/pages
VOLUME ${JETTY_BASE}/oxauth/custom/static
VOLUME ${JETTY_BASE}/oxauth/lib/ext

COPY scripts /opt/scripts
RUN chmod +x /opt/scripts/entrypoint.sh
CMD ["/opt/scripts/entrypoint.sh"]
