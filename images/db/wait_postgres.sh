#!/bin/sh
# make sure pg is ready to accept connections
until pg_isready | grep -q "принимает подключения"
do
  echo "Waiting for postgres"
  sleep 3;
done

# Now able to connect to postgres