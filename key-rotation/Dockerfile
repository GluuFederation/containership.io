FROM ubuntu:14.04

MAINTAINER Gluu Inc. <support@gluu.org>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y --force-yes \
    python \
    python-dev \
    python-pip \
    openjdk-7-jre-headless \
    wget \
    libldap2-dev \
    libsasl2-dev \
    swig \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# JAR files required to generate OpenID Connect keys
RUN mkdir -p /opt/key-rotation/javalibs
RUN wget -q http://ox.gluu.org/maven/org/xdi/oxauth-client/3.1.0-SNAPSHOT/oxauth-client-3.1.0-SNAPSHOT-jar-with-dependencies.jar -O /opt/key-rotation/javalibs/keygen.jar

RUN pip install -U pip

# A workaround to address https://github.com/docker/docker-py/issues/1054
# and to make sure latest pip is being used, not from OS one
ENV PYTHONPATH="/usr/local/lib/python2.7/dist-packages:/usr/lib/python2.7/dist-packages"

WORKDIR /opt/key-rotation

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.py ./

RUN mkdir -p /etc/certs

ENV GLUU_KV_HOST localhost
ENV GLUU_KV_PORT 8500
ENV GLUU_LDAP_URL localhost:8500
ENV GLUU_KEY_ROTATION_INTERVAL 2

ENTRYPOINT ["python", "./entrypoint.py"]
