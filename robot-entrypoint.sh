#!/bin/sh
set -e
set -- python3 -m TUC "$@"

exec "$@"