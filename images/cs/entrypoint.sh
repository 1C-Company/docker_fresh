#!/bin/bash

set -em

#Postgres
echo "Starting Postgres ..."

if [ ! -d "$PGDATA" ]; then
    echo "Postgres - creating a database cluster"
    mkdir "$PGDATA"
    chown -R postgres:postgres "$PGDATA"
    gosu postgres initdb --locale=ru_RU.UTF-8
    echo "synchronous_commit = off" >> "$PGDATA/postgresql.conf"
    exec gosu postgres postgres &
    until psql -h localhost -U "postgres" -c '\q'; do
        echo "Postgres is unavailable - sleeping"
        sleep 1
    done
    echo "Postgres is up"
    gosu postgres psql -c "CREATE USER cs WITH PASSWORD 'cs-pass';"
    gosu postgres psql -c "CREATE DATABASE cs_db OWNER cs ENCODING='UTF8' LC_CTYPE='ru_RU.utf8' TEMPLATE=template0;"
    gosu postgres psql -d cs_db -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
    gosu postgres psql -d cs_db -c 'GRANT USAGE, CREATE ON SCHEMA public TO cs;'
else
    chown -R postgres:postgres "$PGDATA"
    exec gosu postgres postgres &
    until psql -h localhost -U "postgres" -c '\q'; do
        echo "Postgres is unavailable - sleeping"
        sleep 1
    done
    echo "Postgres is up"
fi

#Hazelcast
echo "Starting Hazelcast ..."
HAZELCAST_PATH=$(ls /opt/1C/1CE/components/ | grep "1c-cs-hazelcast")
HAZELCAST="/opt/1C/1CE/components/$HAZELCAST_PATH/bin/launcher start --daemon --procname 1ce-hc-launcher --servicename 1ce-hc --cout $INSTANCE/hc/logs/sysout.log --cerr $INSTANCE/hc/logs/syserr.log --instance $INSTANCE/hc"
HAZELCAST_PID_FILE="$INSTANCE/hc/daemon.pid"

if [ -f "$HAZELCAST_PID_FILE" ]; then
    rm $HAZELCAST_PID_FILE
fi

if [ ! -d "$INSTANCE/hc" ]; then
    echo "Hazelcast - creating an instance"
    mkdir -p "$INSTANCE/hc"
    ring hazelcast instance create --dir $INSTANCE/hc --owner usr1ce
fi
chown -R usr1ce "$INSTANCE/hc"
gosu usr1ce $HAZELCAST

#Elasticsearch
echo "Starting Elasticsearch ..."
ELASTICSEARCH_PATH=$(ls /opt/1C/1CE/components/ | grep "1c-cs-elasticsearch")
MAX_LOCKED_MEMORY=unlimited
MAX_OPEN_FILES=65536
MAX_MAP_COUNT=262144
ELASTICSEARCH="/opt/1C/1CE/components/$ELASTICSEARCH_PATH/bin/launcher start --daemon --procname 1ce-es-launcher --servicename 1ce-es --cout $INSTANCE/es/logs/sysout.log --cerr $INSTANCE/es/logs/syserr.log --instance $INSTANCE/es"
ELASTICSEARCH_PID_FILE="$INSTANCE/es/daemon.pid"

if [ -f "$ELASTICSEARCH_PID_FILE" ]; then
    rm $ELASTICSEARCH_PID_FILE
fi

if [ ! -d "$INSTANCE/es" ]; then
    echo "Elasticsearch - creating an instance"
    mkdir -p "$INSTANCE/es"
    ring elasticsearch instance create --dir $INSTANCE/es --owner usr1ce
fi
chown -R usr1ce "$INSTANCE/es"
gosu usr1ce $ELASTICSEARCH

#CS
echo "Starting CS ..."
CS_PATH=$(ls /opt/1C/1CE/components/ | grep "1c-cs-server-small")
CS="/opt/1C/1CE/components/$CS_PATH/bin/launcher start --procname 1ce-cs-launcher --servicename 1ce-cs --cout $INSTANCE/cs/logs/sysout.log --cerr $INSTANCE/cs/logs/syserr.log --instance $INSTANCE/cs"
CS_PID_FILE="$INSTANCE/cs/daemon.pid"

if [ -f "$CS_PID_FILE" ]; then
    rm $CS_PID_FILE
fi

if [ ! -d "$INSTANCE/cs" ]; then
    echo "CS - creating an instance"
    mkdir -p "$INSTANCE/cs"
    chown -R usr1ce "$INSTANCE/cs"
    ring cs instance create --dir $INSTANCE/cs
    ring cs --instance cs jdbc pools --name common set-params --url jdbc:postgresql://localhost:5432/cs_db?currentSchema=public
    ring cs --instance cs jdbc pools --name common set-params --username cs
    ring cs --instance cs jdbc pools --name common set-params --password cs-pass
    ring cs --instance cs jdbc pools --name privileged set-params --url jdbc:postgresql://localhost:5432/cs_db?currentSchema=public
    ring cs --instance cs jdbc pools --name privileged set-params --username cs
    ring cs --instance cs jdbc pools --name privileged set-params --password cs-pass
    ring cs --instance cs websocket set-params --hostname $(hostname -f)
    ring cs --instance cs websocket set-params --port 9094
    ring cs --instance cs integration set-params --public-url https://$(hostname -f)
    ring cs --instance cs integration set-params --port 8888
    if [ -n "${PUBLISHER_API_KEY}" ]; then
        ring cs --instance cs push set-params --url https://pushnotifications.1c.com/api/push/v1 --publisher-api-key "${PUBLISHER_API_KEY}"
    fi
    gosu usr1ce $CS &
    until curl -sf -X POST -H "Content-Type: application/json" -d "{ \"url\" : \"jdbc:postgresql://localhost:5432/cs_db\", \"username\" : \"cs\", \"password\" : \"cs-pass\", \"enabled\" : true }" -u admin:admin http://localhost:8087/admin/bucket_server; do
        echo "CS is unavailable - sleeping"
        sleep 1
    done
    echo "CS is up"
    fg %2
else
    chown -R usr1ce "$INSTANCE/cs"
    sed -i "s/hostname: .*/hostname: $(hostname -f)/" /var/cs/cs/config/websocket.yml
    gosu usr1ce $CS
fi
