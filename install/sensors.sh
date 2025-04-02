#!/bin/bash

set -e

version="1.0.12"

show_help() {
    echo "Usage: ./install-sensors-xdc.sh [flags] [optional: nodes]"
    echo ""
    echo "This command installs sensors on the nodes attached to the xdc this is run in"
    echo ""
    echo "-h/--help shows this menu"
    echo ""
    echo "[nodes] are optional. They specify the nodes to install the sensors on. If none are given, the sensors are installed on all the nodes"
    echo ""
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    shift
fi

xdc=$(cat /etc/hostname | sed 's/-.*//')
nodes="$@"

if [ "$nodes" = "" ]; then
    nodes=$(mrg show mat -j $(mrg list xdc -j | jq -r ".XDCs[] | select(.name==\"$xdc\") | .materialization" ) | grep node | awk '{print $2}' | sed 's/.$//' | sort | uniq | sed 's/"//g')
fi

# Copy the deb from the package registry
curl "https://gitlab.com/api/v4/projects/53927750/packages/generic/Ubuntu/$version/DataSorcerers.deb" --output $HOME/Sorcerers.deb

for node in $nodes; do
    if [ "$node" = "ifr0" ]  || [ "$node" = "ifr1" ] || [ "$node" = "fusioncore" ]; then
        continue
    fi
    (
        echo "installing on $node"
        # Copy the deb to all the nodes
        scp $HOME/Sorcerers.deb "$node:$HOME/Sorcerers.deb"
        # Build the deb on all the nodes
        ssh $node "sudo dpkg -i $HOME/Sorcerers.deb || sudo apt install -f -y"
        # remove the package corpse
        ssh $node "rm $HOME/Sorcerers.deb"
    ) &
done

wait
