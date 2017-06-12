FROM ubuntu:14.04

MAINTAINER Shouro <shouro@gluu.org>


#RUN groupadd -r ldap && useradd -r -g ldap ldap


RUN apt-get update && apt-get install -y \
    wget \
    curl \
    python \
    python-pip \
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


WORKDIR /ldap

#configure_openldap
RUN mkdir -p /opt/symas/etc/openldap
RUN mkdir -p /opt/gluu/schema/openldap
RUN mkdir -p /etc/cert

COPY schema /opt/gluu/schema/openldap
COPY templates ./templates
COPY static ./static
COPY scripts ./scripts
RUN cp ./templates/symas-openldap.conf /opt/symas/etc/openldap/symas-openldap.conf

# Install requirements
RUN pip install --no-cache-dir -r ./scripts/requirements.txt

# Data dir
RUN mkdir -p /opt/gluu/data/main_db
RUN mkdir -p /opt/gluu/data/site_db

# TODO: currently using port 1636 but will change to 1389
EXPOSE 1636
#EXPOSE 1389

# Entrypoint
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
