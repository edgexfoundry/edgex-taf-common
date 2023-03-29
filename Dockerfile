#
# Copyright (c) 2022
# IOTech
#
# SPDX-License-Identifier: Apache-2.0
#
FROM alpine:3.16

LABEL license='SPDX-License-Identifier: Apache-2.0' \
  copyright='Copyright (c) 2022: IOTech'

LABEL maintainer="Bruce Huang <bruce@iotechsys.com>"

COPY . /edgex-taf/edgex-taf-common
COPY robot-entrypoint.sh /usr/local/bin/

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
    apk add --no-cache python3-dev g++ zeromq-dev=4.3.4-r0  &&  \
    \
    # install Python
    apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    apk add --no-cache tzdata      &&  \
    cp /usr/share/zoneinfo/UTC /etc/localtime  &&  \
    apk del tzdata  &&  \
    \
    # install pip
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    \
    # Install robotframework and required libraries
    pip3 install ./edgex-taf-common  &&  \
    pip3 install robotframework==4.1.3 && \
    pip3 install docker==4.4.1  &&  \
    pip3 install -U python-dotenv==0.15.0  &&  \
    pip3 install -U RESTinstance==1.0.2  &&  \
    pip3 install -U robotbackgroundlogger==1.2  &&  \
    pip3 install -U configparser==5.0.1  &&  \
    pip3 install -U requests==2.25.1 &&  \
    pip3 install -U robotframework-requests==0.8.0  &&  \
    pip3 install -U paho-mqtt==1.5.1  &&  \
    pip3 install -U redis==4.5.3  &&  \
    pip3 install -U pyzmq==22.2.1  &&  \
    pip3 install -U robotframework-seleniumlibrary==5.1.3  && \
    pip3 install -U psycopg2==2.9.3  && \
    pip3 install -U numpy==1.22.3 && \
    pip3 install -U psutil==5.9.0  && \
    pip3 install -U pycryptodome==3.15.0 && \
    pip3 install -U influxdb-client==1.33.0

ENTRYPOINT ["sh", "/usr/local/bin/robot-entrypoint.sh"]
