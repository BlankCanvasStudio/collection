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



query = f'import "influxdata/influxdb/schema"\n schema.measurements(bucket: "{bucket}")'

result = query_api.query(query)

# Extract and print measurements
measurements = [record.get_value() for table in result for record in table.records]
print(measurements)

# Verifying the values in cmds record. Just pulling out 20 records
query = '''
from(bucket: "DISCERN")
  |> range(start: -1y)
  |> filter(fn: (r) => r["_measurement"] == "os")
  |> limit(n: 20)
'''

print("Reading 20 results from the OS table")
tables = query_api.query(query)
for table in tables:
    for record in table.records:
        print(record.values)
print("\n\n")

