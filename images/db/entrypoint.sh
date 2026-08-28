#!/bin/bash

set -e

if [ "$1" = 'postgres' ]; then
    chown -R postgres:postgres "$PGDATA" /var/run/postgresql
    if [ ! -s "$PGDATA/PG_VERSION" ]; then
        gosu postgres initdb
        echo "listen_addresses = '*'" >> "$PGDATA/postgresql.conf"
        echo "port = 5432" >> "$PGDATA/postgresql.conf"
        echo "synchronous_commit = off" >> "$PGDATA/postgresql.conf"
        echo "log_destination = 'stderr'" >> "$PGDATA/postgresql.conf"
        echo "log_min_messages = warning" >> "$PGDATA/postgresql.conf"
        echo "log_min_error_statement = error" >> "$PGDATA/postgresql.conf"
        echo "log_timezone = 'Europe/Moscow'" >> "$PGDATA/postgresql.conf"
        echo "log_line_prefix = '%t [%p]: [%l],user=%u,db=%d,app=%a,client=%h '" >> "$PGDATA/postgresql.conf"
        echo "log_connections = on" >> "$PGDATA/postgresql.conf"
        echo "log_disconnections = on" >> "$PGDATA/postgresql.conf"
        sed -i 's/max_connections = 100/max_connections = 1000/' "$PGDATA/postgresql.conf"
        echo "host    all             all             0.0.0.0/0               trust" >> "$PGDATA/pg_hba.conf"
    fi

    exec gosu postgres postgres -c jit=off
fi

exec "$@"
