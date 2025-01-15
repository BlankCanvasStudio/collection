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


# Verifying the values in cmds record
query = '''
from(bucket: "DISCERN")
  |> range(start: -1y)
  |> filter(fn: (r) => r["_measurement"] == "bash")
  |> limit(n: 20)
'''
print("query 1")
tables = query_api.query(query)
for table in tables:
    for record in table.records:
        print(record.values)
print("\n\n")



# # List all the fields  we have in the measurement
# query = 'from(bucket: "DISCERN") \
#             |> range(start: -1y) \
#             |> filter(fn: (r) => r["_measurement"] == "bash") \
#             |> group(columns: ["Cmds"]) \
#             |> limit(n: 10)'
# print("query 2")
# tables = query_api.query(query)
# for table in tables:
#     for record in table.records:
#         print(record.values)
# print("\n\n")


query = f'from(bucket: "DISCERN") \
          |> range(start: -1y) \
          |> filter(fn: (r) => r["_measurement"] == "bash" and type(v: r["Cmds"]) == "string") \
          |> group(columns: [ "Count" ]) \
          |> keep(columns: [ "_time", "Cmds", "Count" ])'


# Print those devices
print("query 3")
tables = query_api.query(query)
for table in tables:
    for record in table:
        print(record)
    print()
print("\n\n")

