#!/bin/sh
set -e
cp -r /edgex-taf/edgex-taf-common .
set -- python3 edgex-taf-common/TAF-Manager/trigger/run.py "$@"

exec "$@"