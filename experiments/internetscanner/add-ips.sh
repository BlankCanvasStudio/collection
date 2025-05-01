#!/bin/bash

node_kinds=13

copies=2

total_nodes=$((node_kinds * copies))


node_types=(\
 "postgres" \
 "mysql" \
 "tomcat" \
 "nginx" \
 "outlook" \
 "wordpress" \
 "dns" \
 "pop3" \
 "smtp" \
 "telnet" \
 "vnc" \
 "mysqlwebhost" \
 "pgwebhost" \
)

index=0
copy_index=0

for ip in 107.125.{128..255}.{2..255}; do
    # Drop 1/4 of all IPs randomly
    if [ "$((RANDOM % 4 + 1))" != "0" ]; then
        (
            node_index=$((RANDOM % $node_kinds))
            version=$(($index % $total_nodes)) 

            ssh "${node_types[node_index]}$((copy_index + 1))" "sudo ip addr add $ip/17 dev eth1"

        ) &
    fi

    index=$(($index + 1))
    copy_index=$((($copy_index + 1) % $copies))

    if [ "$(($index % 500))" = "0" ]; then
        echo "Added 500 ips"
        wait
    fi
done

