#!/bin/bash

set -e

if [ "$2" = 'nodebug' ]
then
    DEBUG_1C=""
else
    DEBUG_1C="-debug -http"
fi

#chmod 777 -R /var/dumps

if ls /mnt/*.cf 1> /dev/null 2>&1; then
    chmod 777 -R /mnt/*.cf
fi

#if ls /mnt/*.dt 1> /dev/null 2>&1; then
#    chmod 777 -R /mnt/*.dt
#fi

#chmod 777 -R /volumes
#echo '/var/dumps/%e.%t.%p.core' > /proc/sys/kernel/core_pattern
#ulimit -c unlimited

if [ "$1" = 'srv' ]
then
    chown -R usr1cv8:grp1cv8 ${DATA_1C} ${LOGS_1C}
    chown -R usr1cv8:grp1cv8 /var/1C/licenses
    exec gosu usr1cv8 /opt/1c/ragent ${DEBUG_1C} /d ${DATA_1C} /port ${AGENT_PORT} /regport ${AGENT_REGPORT} /range ${AGENT_RANGE}
elif [ "$1" = 'srv+cli' ]
then
    chown -R usr1cv8:grp1cv8 ${DATA_1C} ${LOGS_1C}
    chown -R usr1cv8:grp1cv8 /var/1C/licenses
    exec gosu usr1cv8 /opt/1c/ragent ${DEBUG_1C} /d ${DATA_1C} /port ${AGENT_PORT} /regport ${AGENT_REGPORT} /range ${AGENT_RANGE} &
    status=$?
    if [ $status -ne 0 ]; then
        echo "Failed to start ragent: $status"
        exit $status
    fi

    exec /usr/bin/Xvfb ${DISPLAY} -screen 0 1680x1050x24 -shmem &
    exec /usr/bin/x11vnc -forever -noxfixes &
    sleep 5
    exec startxfce4 &
    status=$?
    if [ $status -ne 0 ]; then
        echo "Failed to start Xvfb: $status"
        exit $status
    fi
    while sleep 60; do
        if ! pgrep -x ragent > /dev/null 2>&1; then
            echo "One of the processes has already exited (ragent)."
            exit 1
        fi
        if ! pgrep -x Xvfb > /dev/null 2>&1; then
            echo "One of the processes has already exited (Xvfb)."
            exit 1
        fi
    done
elif [ "$1" = 'cli' ]
then
    chown -R usr1cv8:grp1cv8 ${LOGS_1C}
    exec /usr/bin/Xvfb ${DISPLAY} -screen 0 1680x1050x24 -shmem &
    exec /usr/bin/x11vnc -forever -noxfixes &
    sleep 5
    exec startxfce4
fi

command=$(echo $@ | sed -En 's/^cli //p')
exec $command
