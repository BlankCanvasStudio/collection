#!/bin/python3

from datetime import datetime, timezone, timedelta
import pytz, sys

import data_util

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

measurement="file"

OpDefinitions = {
    '1': "create",
    '2': "write", 
    '4': "remove", 
    '8': "rename", 
    '16': "chmod", 
}


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


# Count how many measurements were taken
query = f'''
from(bucket: "DISCERN")
  |> range(start: -1y)
  |> filter(fn: (r) => r["_measurement"] == "{measurement}")
  |> count()
'''


query = '''
from(bucket: "DISCERN") 
    |> range(start: -1y) 
    |> filter(fn: (r) => r["_measurement"] == "file")
    |> max(column: "_time")
'''
tables = query_api.query(query)
for table in tables:
    for record in table.records:
        print(record)


num_points = 0  # Initialize num_points
for table in tables:
    for record in table.records:
        # Check if '_value' exists in record values
        if '_value' not in record.values or record.values['_value'] == None:
            continue

        num_points += int(record.values['_value'])

print(f"number of {measurement} points recorded: {num_points} over a {time} period")
print("")


# Get unique operations
query = f'''
from(bucket: "DISCERN")
  |> range(start: -1y)
  |> filter(fn: (r) => r["_measurement"] == "file")
  |> keep(columns: ["Op"]) // Keep only the "Op" tag
  |> distinct(column: "Op") // Extract unique "Op" values
'''

ops = []
tables = query_api.query(query)
for table in tables:
    for record in table.records:
        ops += [record['Op']]

for op in ops:
    num_ops=0

    # Count how many times this operation happened
    query = f'''
    from(bucket: "DISCERN")
      |> range(start: -1y)
      |> filter(fn: (r) => r["_measurement"] == "file")
      |> filter(fn: (r) => r["Op"] == "{op}")
      |> count()
    '''

    tables = query_api.query(query)
    for table in tables:
        for record in table.records:
            num_ops += int(record['_value'])


    # Get the measurements for every time this happened
    query = f'''
    from(bucket: "DISCERN")
      |> range(start: -1y)
      |> filter(fn: (r) => r["_measurement"] == "file")
      |> filter(fn: (r) => r["Op"] == "{op}")
      |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''


    avg_size = 0
    num_records = 0

    # Calculate the average size of this kind of query
    tables = query_api.query(query)
    for table in tables:
        for record in table.records:
            keys = tables[0].records[0].values.keys()
            for key in keys:
                if not data_util.valid_column(key):
                    continue
                val = tables[0].records[0].values[key]
                avg_size += data_util.find_size(val)
            num_records += 1

    if num_records:
        avg_size /= num_records

    # Print out this useful information
    print(f"File op {OpDefinitions[op]} happened {num_ops} times. Estimated size of {avg_size} Bytes")

print("")


# Print a sample of what the data structure looks like
try:
    output = "fields are:\n"

    keys = tables[0].records[0].values.keys()
    for key in keys:
        if not data_util.valid_column(key):
            continue
        val = tables[0].records[0].values[key]
        kind = type(val)
        size = data_util.find_size(val)
        output += f"\t{key}: {kind} ({size}B)\n"

    print(output)

except Exception as e:
    print(e)
    pass

