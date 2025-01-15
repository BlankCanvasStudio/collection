#!/bin/bash

fusioncore="fusioncore"

show_help() {
    echo "Usage: ./util/empty-databases.sh [flags] <fusion node>"
    echo ""
    echo "This command empties the databases at the <fusion node>"
    echo "This means you can easily stand up the databases for post hoc analysis"
    echo ""
    echo "-h/--help shows this menu"
    echo ""
    echo "<fusion node> optionally allows you to specify the node you'd like to download the data from."
    echo "    defaults to fusioncore"
    echo ""
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    shift
fi

if [ ! "$1" = "" ]; then
    fusioncore="$1"
    shift
fi

if [ ! "$@" = "" ]; then
    echo "more than 1 argument supplied. should you use quotes?"
    exit 1
fi

ssh "$fusioncore" "sudo systemctl stop FusionCore"

ssh "$fusioncore" "docker stop discerninflux || true"
ssh "$fusioncore" "docker stop discernpsql || true"

ssh "$fusioncore" "docker rm discerninflux"
ssh "$fusioncore" "docker rm discernpsql"

ssh "$fusioncore" "docker volume rm discerninflux"
ssh "$fusioncore" "docker volume rm discernpsql"

ssh "$fusioncore" "sudo systemctl restart FusionCore"



