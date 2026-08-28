#!/bin/bash

set -em

export DISPLAY=:99
/usr/bin/Xvfb ${DISPLAY} -screen 0 1680x1050x24 &
/usr/bin/x11vnc -forever -noxfixes &
sleep 5
startxfce4 &
status=$?
if [ $status -ne 0 ]; then
    echo "Failed to start Xvfb: $status"
    exit $status
fi

if [ "$CONTAINER_NAME" = 'srv' ]
then
    echo "Starting Executor in $CONTAINER_NAME"
    chown -R usr1cv8:grp1cv8 ${COREDATA} ${CORELOGS} ${LIC_DATA} ${MNT_PATH} #${EXECUTOR_DATA} ${EXECUTOR_HOME} ${VOLUMES_PATH} ${DUMP_PATH}
    if [ ! -f "${EXECUTOR_DATA}/Linux_Server_Start.sh" ]
    then
        exec gosu usr1cv8 ragent -debug -http -d ${COREDATA}
    else
        exec gosu usr1cv8 ragent -debug -http -d ${COREDATA} &
        while [ ! -f "${EXECUTOR_DATA}/data/connection_settings.json" ]
        do
            sleep 1
        done
        exec gosu usr1cv8 ${EXECUTOR_DATA}/Linux_Server_Start.sh &
        fg %1
    fi
elif [ "$CONTAINER_NAME" = 'ras' ]
then
    echo "Working in $CONTAINER_NAME"
    chown -R usr1cv8:grp1cv8 ${CORELOGS}
    exec gosu usr1cv8 "$@"
elif [ "$CONTAINER_NAME" = 'web' ]
then
    echo "Starting Executor in $CONTAINER_NAME"
    chown -R www-data:www-data ${CORELOGS} #${EXECUTOR_DATA} ${EXECUTOR_HOME} ${FRESH}
    if [ ! -f "${EXECUTOR_DATA}/Linux_Server_Start.sh" ]
    then
        exec apachectl -DFOREGROUND
    else
        exec apachectl -DFOREGROUND &
        while [ ! -f "${EXECUTOR_DATA}/data/connection_settings.json" ]
        do
            sleep 1
        done
        exec gosu www-data ${EXECUTOR_DATA}/Linux_Server_Start.sh &
        fg %1
    fi
fi

exec "$@"