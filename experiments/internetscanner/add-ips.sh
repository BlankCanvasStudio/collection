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
copy_index=1

for ip in 107.125.{128..255}.{2..255}; do
    version=$(($index % $total_nodes)) 
    node_index=$(($index % $copies)) 

    ssh "${node_types[node_index]}${copy_index}" "sudo ip addr add $ip/17 dev eth1"

    index=$(($index + 1))
    copy_index=$(((($copy_index + 1) % $copies) + 1))
done

