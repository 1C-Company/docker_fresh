#!/bin/sh
rm -rf /var/opt/1C/1CE/instances/1c-enterprise-esb/daemon.pid
exec "$@"
