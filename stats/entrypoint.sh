#!/bin/sh

handler() {
    if [ -z "$pid" ]; then
        return
    fi

    kill "$pid"
    exit
}

trap handler TERM

while true; do
    curl \
        --header "Authorization: Token $DRF_TOKEN" \
        --header "Host: $DOMAIN_NAME" \
        --request POST \
        --silent \
        "ui:$UI_PORT/xray/stats/"

    sleep "$STATS_INTERVAL" &
    pid="$!"
    wait "$pid"
done
