#!/bin/bash

set -e

fusioncore="fusioncore"

show_help() {
    echo "Usage: ./util/download/databases.sh [flags] <fusion core node>"
    echo ""
    echo "This command exfiltrates data from the fusioncore node attached to the current xdc"
    echo ""
    echo "-h/--help shows this menu"
    echo ""
    echo "<fusion core node> is optional. defaults to 'fusioncore'"
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
    echo "more arguments passed than just the fusion core node. should you add quotes?"
    echo "exiting"
    exit 1
fi


# Backup and gzip in old container
echo ""
echo "building influx backup"
echo ""
ssh $fusioncore 'docker exec discerninflux sh -c "influx backup --token \"<token>\" /backup"'
ssh $fusioncore 'docker exec discerninflux sh -c "tar -czf /backup.tar.gz -C / backup"'

# Copy gzipped backup to host
echo ""
echo "copying off influx backup"
echo ""
ssh $fusioncore 'docker cp discerninflux:/backup.tar.gz ~/influx-data.tar.gz'

scp $fusioncore:~/influx-data.tar.gz ~/influx-data.tar.gz
ssh $fusioncore "rm ~/influx-data.tar.gz"


echo ""
echo "dumping postgres database"
echo ""
ssh $fusioncore 'docker exec discernpsql pg_dump -U postgres -d Discern > ~/postgres-data.sql'


echo ""
echo "moving dump to xdc"
echo ""
scp $fusioncore:~/postgres-data.sql ~/postgres-data.sql
ssh $fusioncore 'rm ~/postgres-data.sql'

