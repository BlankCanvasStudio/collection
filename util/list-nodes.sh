#!/bin/bash
xdc=$(cat /etc/hostname | sed 's/-.*//')
output=$(mrg show mat -j $(mrg list xdc -j | jq -r ".XDCs[] | select(.name==\"$xdc\") | .materialization" ) | grep node | awk '{print $2}' | sed 's/.$//' | sort | uniq | sed 's/"//g')

for node in $output; do 
    if [ "$node" = "ifr0" ]  || [ "$node" = "ifr1" ] || [ "$node" = "fusioncore" ]; then
        continue
    fi
    echo $node
done

