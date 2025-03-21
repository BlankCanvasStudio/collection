#!/bin/bash

set -e

version="0.3.13"

show_help() {
    echo "Usage: ./install-core.sh [flags] <node>"
    echo ""
    echo "This command installs the fusion core on the specified node"
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

node=$1
if [ "$node" = "" ]; then
    echo ""
    echo "node cannot be empty"
    echo "exiting"
    echo ""
    exit 1
fi
shift

if [ ! "$@" = "" ]; then
    echo "more arguments passed than just the node. should you add quotes?"
    echo "exiting"
    exit 1
fi

# Download the fusion core debian
curl "https://gitlab.com/api/v4/projects/53927750/packages/generic/Ubuntu/$version/FusionCore.deb" --output $HOME/FusionCore.deb

# Copy the deb to the node
scp $HOME/FusionCore.deb "$node:$HOME/FusionCore.deb"
# Build the deb on all the node
ssh $node "sudo dpkg -i $HOME/FusionCore.deb || sudo apt install -f -y"
# remove the package corpse
ssh $node "rm $HOME/FusionCore.deb"

