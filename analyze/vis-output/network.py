#!/bin/python3

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# Set up the influx connection
url = "http://10.10.10.4:8086"
token = "BIGElHSa291FOkrliGaBVc7ksnGgQ4vALbkfJzRuH02T2XB8qouH0H3IkYTJACE-XZ-QYV664CH5655LkbQDIQ"
org = "ISI"
bucket = "DISCERN"

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()


# List all the devices we have recorded in influx:
query = f'from(bucket: "DISCERN") \
          |> range(start: -1y) \
          |> filter(fn: (r) => r["_measurement"] == "network") \
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") \
          |> group() \
          |> distinct(column: "DevID") \
          |> yield()'


# Print those devices
Dev = None
tables = query_api.query(query)
for table in tables:
    for record in table.records:
        print(record)
        Dev = record["_value"]

print(f"dev found: .{Dev}.")


# Find the mac addresses that device sent to 
query = f'from(bucket:"{bucket}") \
             |> range(start: -1y) \
             |> filter(fn: (r) => r["_measurement"] == "network") \
             |> filter(fn: (r) => r.DevID == "{Dev}") \
             |> keep(columns: [ "_time", "DevID", "DST_MAC"]) \
             |> distinct(column: "DST_MAC")'
 
tables = query_api.query(query)

MACs = []

for table in tables:
    for record in table.records:
        if record.values.get('DST_MAC') == None: continue
        MACs += [ record.values.get('DST_MAC') ]

print("Communicated with: ", ", ".join(MACs))


# Find when those devices communicated
for mac in MACs:
    query = f'from(bucket:"{bucket}") \
                 |> range(start: -1y) \
                 |> filter(fn: (r) => r["_measurement"] == "network") \
                 |> filter(fn: (r) => r.DevID == "{Dev}" and r.DST_MAC == "{mac}") \
                 |> keep(columns: [ "_time"])'
     
    tables = query_api.query(query)

    times = []
    for table in tables:
        for record in table.records:
            times += [ record.values.get('_time') ]

    print(f"dev {Dev}")
    print(f"communicated with: {mac}")
    for time in times:
        print(f"   {time}")


# Find the link layer protocol when they communicate
for mac in MACs:
    query = f'from(bucket:"{bucket}") \
                 |> range(start: -1y) \
                 |> filter(fn: (r) => r["_measurement"] == "network") \
                 |> filter(fn: (r) => r.DevID == "{Dev}" and r.DST_MAC == "{mac}") \
                 |> keep(columns: [ "_time", "LinkProtocol", "NetworkProtocol", "TransportProtocol", "ApplicationProtocol" ])'
     
    tables = query_api.query(query)

    protocols = []
    for table in tables:
        for record in table.records:
            protocol = str(record.values.get('_time'))

            if record.values.get('LinkProtocol') != None: 
                protocol += ": " + record.values.get('LinkProtocol') 
            if record.values.get('NetworkProtocol') != None: 
                protocol += ", " + record.values.get('NetworkProtocol')
            if record.values.get('TransportProtocol') != None: 
                protocol += ", " + record.values.get('TransportProtocol')
            if record.values.get('ApplicationProtocol') != None: 
                protocol += ", " + record.values.get('ApplicationProtocol')

            protocols += [ protocol ]

        print(f"dev {Dev}")
        print(f"communicated with: {mac}")
        for protocol in protocols:
            print(f"   {protocol}")

