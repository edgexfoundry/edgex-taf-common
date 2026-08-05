#
# Copyright (c) 2022
# IOTech
#
# SPDX-License-Identifier: Apache-2.0
#
FROM alpine:3.22.1

LABEL license='SPDX-License-Identifier: Apache-2.0' \
  copyright='Copyright (c) 2022: IOTech'

LABEL maintainer="Bruce Huang <bruce@iotechsys.com>"

COPY . /edgex-taf/edgex-taf-common
COPY robot-entrypoint.sh /usr/local/bin/
COPY requirements.txt /edgex-taf/requirements.txt

WORKDIR /edgex-taf

RUN sed -e 's/dl-cdn[.]alpinelinux.org/dl-4.alpinelinux.org/g' -i~ /etc/apk/repositories

RUN apk upgrade && apk add --update --no-cache openssl curl jq docker-cli && \
    # **** install chromedriver ****
    apk add --no-cache chromium chromium-chromedriver && \
    \
    # Add packages for psycopg2
    apk add --no-cache libc-dev libffi-dev postgresql-dev gcc musl-dev && \
    \
    # Update packages for RESTinstance and pyzmq
    apk add --no-cache python3-dev g++ zeromq-dev=4.3.5-r2  &&  \
    \
    # install Python
    apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    apk add --no-cache tzdata  &&  \
    cp /usr/share/zoneinfo/UTC /etc/localtime  &&  \
    apk del tzdata  &&  \
    \
    # install pip
    rm /usr/lib/python*/EXTERNALLY-MANAGED && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache-dir --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    \
    # Install robotframework and required libraries
    pip3 install --no-cache-dir ./edgex-taf-common  &&  \
    pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["sh", "/usr/local/bin/robot-entrypoint.sh"]
