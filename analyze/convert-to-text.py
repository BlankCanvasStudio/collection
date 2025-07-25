#!/usr/bin/env python3

import influxdb_client, json, os
from influxdb_client.client.write_api import SYNCHRONOUS

network_data_file = "network-data.json"
cpu_data_file = "cpu-data.json"
interface_data_file = "interface-data.json"
file_data_file = "file-data.json"
proc_mem_data_file = "proc-mem-data.json"
proc_new_data_file = "proc-new-data.json"

# Set up the influx connection
url = "http://10.10.10.4:8086"
token = ""
org = "ISI"
bucket = "DISCERN"

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org,
    timeout=360000,
)

write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

if os.path.exists(network_data_file):
    os.remove(network_data_file)

if os.path.exists(cpu_data_file):
    os.remove(cpu_data_file)

if os.path.exists(interface_data_file):
    os.remove(interface_data_file)

if os.path.exists(file_data_file):
    os.remove(file_data_file)

if os.path.exists(proc_mem_data_file):
    os.remove(proc_mem_data_file)

if os.path.exists(proc_new_data_file):
    os.remove(proc_new_data_file)



#
# Write the network data to file
#

query = f'''
from(bucket: "DISCERN")
  |> range(start: -1y)
  |> filter(fn: (r) => r["_measurement"] == "network")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
'''


results = []

tables = query_api.query(query)
for table in tables:
    for record in table.records:
        dict_record = record.values
        del dict_record['result']
        del dict_record['table']
        # del dict_record['_value']
        # del dict_record['_field']
        del dict_record['_measurement']
        del dict_record['_start']
        del dict_record['_stop']
        results += [ dict_record ]


with open(network_data_file, 'w') as fd:
    for el in results:
        fd.write(json.dumps(el, default=str) + "\n")



#
# Write the cpu data to file
#

query = f'''
from(bucket: "DISCERN")
  |> range(start: -1y)
  |> filter(fn: (r) => r["_measurement"] == "cpu-load")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
'''


results = []

query_api = client.query_api()

tables = query_api.query(query)
for table in tables:
    for record in table.records:
        dict_record = record.values
        del dict_record['result']
        del dict_record['table']
        # del dict_record['_field']
        del dict_record['_measurement']
        del dict_record['_start']
        del dict_record['_stop']
        results += [ dict_record ]


with open(cpu_data_file, 'w') as fd:
    for el in results:
        fd.write(json.dumps(el, default=str) + "\n")




Write the interface data to file


query = f'''
from(bucket: "DISCERN")
  |> range(start: -1y)
  |> filter(fn: (r) => r["_measurement"] == "interfaces")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
'''


results = []

query_api = client.query_api()

tables = query_api.query(query)
for table in tables:
    for record in table.records:
        dict_record = record.values
        del dict_record['result']
        del dict_record['table']
        # del dict_record['_field']
        del dict_record['_measurement']
        # del dict_record['_value']
        del dict_record['_start']
        del dict_record['_stop']
        results += [ dict_record ]


with open(interface_data_file, 'w') as fd:
    for el in results:
        fd.write(json.dumps(el, default=str) + "\n")



#
# Write the file data to file
#

"""
query = f'''
from(bucket: "DISCERN")
  |> range(start: -1y)
  |> filter(fn: (r) => r["_measurement"] == "file-hash")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
'''


results = []

query_api = client.query_api()

tables = query_api.query(query)
for table in tables:
    for record in table.records:
        dict_record = record.values
        del dict_record['result']
        del dict_record['table']
        # del dict_record['_field']
        del dict_record['_measurement']
        # del dict_record['_value']
        del dict_record['_start']
        del dict_record['_stop']
        results += [ dict_record ]


with open(file_data_file, 'w') as fd:
    for el in results:
        fd.write(json.dumps(el, default=str) + "\n")

"""


#
# Write the proc-mem data to file
#

query = f'''
from(bucket: "DISCERN")
  |> range(start: -1y)
  |> filter(fn: (r) => r["_measurement"] == "proc-mem")
  |> pivot(rowKey: ["_time", "Pid"], columnKey: ["_field"], valueColumn: "_value")
'''


results = []

query_api = client.query_api()

tables = query_api.query(query)
# tables = query_api.query_data_frame(query)
for table in tables:
    for record in table.records:
        dict_record = record.values
        del dict_record['result']
        del dict_record['table']
        # del dict_record['_field']
        del dict_record['_measurement']
        # del dict_record['_value']
        del dict_record['_start']
        del dict_record['_stop']
        results += [ dict_record ]


with open(proc_mem_data_file, 'w') as fd:
    for el in results:
        fd.write(json.dumps(el, default=str) + "\n")

 

#
# Write the proc-new data to file
#

query = f'''
from(bucket: "DISCERN")
  |> range(start: -1y)
  |> filter(fn: (r) => r["_measurement"] == "proc-new")
  |> pivot(rowKey: ["_time", "Pid"], columnKey: ["_field"], valueColumn: "_value")
'''


results = []

query_api = client.query_api()

tables = query_api.query(query)
for table in tables:
    for record in table.records:
        dict_record = record.values
        del dict_record['result']
        del dict_record['table']
        # del dict_record['_field']
        del dict_record['_measurement']
        # del dict_record['_value']
        del dict_record['_start']
        del dict_record['_stop']
        results += [ dict_record ]


with open(proc_new_data_file, 'w') as fd:
    for el in results:
        fd.write(json.dumps(el, default=str) + "\n")

