#!/bin/sh
MY_PORT="$(python3 -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()')"
MY_INSTANCE="$CARDBOARD_CR_DB_INSTANCE"
MY_PID=

_csql_cleanup() {
  if [ -n "$MY_PID" ]; then
    kill -15 "$MY_PID"
  fi
}

trap _csql_cleanup EXIT

if lsof -Pi ":$MY_PORT" -sTCP:LISTEN -t >/dev/null; then
    echo "Port $MY_PORT is already in use" >&2
    exit 1
fi

cloud-sql-proxy "$MY_INSTANCE?port=$MY_PORT" &
MY_PID="$!"

while true; do
    if lsof -Pi ":$MY_PORT" -sTCP:LISTEN -t >/dev/null; then
        break
    fi
    # echo "Port not ready yet, checking again"
done

psql --dbname=cardboard -h 127.0.0.1 -p "$MY_PORT" "$@"
