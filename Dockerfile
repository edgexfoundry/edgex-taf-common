#
# Copyright (c) 2021
# IOTech
#
# SPDX-License-Identifier: Apache-2.0
#
ARG DOCKER_VERSION=18.09.5
FROM docker:${DOCKER_VERSION} AS docker-cli

FROM alpine:3.12

LABEL license='SPDX-License-Identifier: Apache-2.0' \
  copyright='Copyright (c) 2021: IOTech'

LABEL maintainer="Bruce Huang <bruce@iotechsys.com>"

COPY --from=docker-cli  /usr/local/bin/docker   /usr/local/bin/docker
COPY . /edgex-taf/edgex-taf-common
COPY robot-entrypoint.sh /usr/local/bin/

WORKDIR /edgex-taf

RUN echo "**** install Python ****" && \
    apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    apk add --no-cache tzdata      &&  \
    cp /usr/share/zoneinfo/UTC /etc/localtime  &&  \
    apk del tzdata  &&  \
    \
    echo "**** install pip ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    \
    echo "**** install robotframework and dependencies ****" && \
    pip3 install ./edgex-taf-common  &&  \
    pip3 install robotframework==3.2.2 && \
    pip3 install docker==4.4.1  &&  \
    pip3 install -U python-dotenv==0.15.0  &&  \
    # install RESTinstance for pytz and yaml library
    pip3 install -U RESTinstance==1.0.2  &&  \
    pip3 install -U robotbackgroundlogger==1.2  &&  \
    pip3 install -U configparser==5.0.1  &&  \
    pip3 install -U requests==2.25.1 &&  \
    pip3 install -U robotframework-requests==0.8.0  &&  \
    pip3 install -U paho-mqtt==1.5.1  &&  \
    pip3 install -U redis==3.5.3  &&  \
    pip3 install -U robotframework-seleniumlibrary==4.5.0  && \
    apk add --no-cache py3-numpy==1.18.4-r0 && \
    apk add --no-cache py3-psutil==5.7.0-r0  && \
    \
    echo "**** install other tools ****" && \
    apk add --no-cache curl && \
    apk add --no-cache openssl && \
    \
    echo "**** install chromedriver ****" && \
    apk update && apk upgrade && \
    echo @latest-stable http://nl.alpinelinux.org/alpine/latest-stable/community >> /etc/apk/repositories && \
    echo @latest-stable http://nl.alpinelinux.org/alpine/latest-stable/main >> /etc/apk/repositories && \
    apk add --no-cache \
    chromium@latest-stable \
    chromium-chromedriver@latest-stable

ENTRYPOINT ["sh", "/usr/local/bin/robot-entrypoint.sh"]
