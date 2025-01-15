#!/bin/python3

from datetime import datetime, timezone, timedelta
import pytz

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

measurement="log"

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

num_points = 0

# Current time as a timezone-aware datetime (UTC)
start = datetime.now(timezone.utc)
# Oldest time as a timezone-aware datetime (epoch start in UTC)
end = datetime(1970, 1, 1, tzinfo=timezone.utc)

tables = query_api.query(query)
num_points = 0  # Initialize num_points
for table in tables:
    for record in table.records:
        # Convert record timestamps to timezone-aware datetimes if necessary
        record_start = record['_start']
        record_stop = record['_stop']
        if record_start.tzinfo is None:
            record_start = record_start.replace(tzinfo=timezone.utc)
        if record_stop.tzinfo is None:
            record_stop = record_stop.replace(tzinfo=timezone.utc)

        # Update start and end times
        if record_start < start:
            start = record_start
        if record_stop > end:
            end = record_stop

        # Check if '_value' exists in record values
        if '_value' not in record.values:
            continue
        if 'Count' in record.values:  # For bash while poorly implemented
            num_points += int(record.values['Count'] * record.values['_value'])
            continue
        num_points += int(record.values['_value'])

print(f"number of {measurement} points recorded: {num_points} over a {end - start} period")

