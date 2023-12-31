from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import dotenv_values
from main import pprint
import os, psutil

config = dotenv_values(".env")
print(config.items())

mempool_bucket = "MemPoolData"

# Create a new influx client instance
client = InfluxDBClient(url=config["INFLUXDB_URL"], token=config["INFLUXDB_API_TOKEN"], org=config["INFLUXDB_ORG"])

write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

current_time = datetime.utcnow()
previous_time_start = current_time - timedelta(minutes=1600)
previous_time_end = current_time - timedelta(minutes=1590)
previous_time_start = int(previous_time_start.timestamp() // 1)
previous_time_end = int(previous_time_end.timestamp() // 1)
print(previous_time_start)
print(previous_time_end)


tables = query_api.query(
    f'''
    from(bucket:"{mempool_bucket}") |> 
    range(start: {previous_time_start}, stop: {previous_time_end}) |>
    sort(columns: ["_time"], desc: true) |>
    limit(n: 5)
    ''')
print(len(tables))
process = psutil.Process()
print(process.memory_info().rss / (1024 ** 2))  

i = 0
for table in tables:
    pprint(table)
    exit(0)
    i += 1
    timestamp = table.records[0].values["_time"]
    # Check if timestamp is an instance of datatime class
    assert(isinstance(timestamp, datetime))
    tx_time: int =  int(timestamp.timestamp() // 1)
    tx_hash = table.records[0].values["TxHash"]
    pprint({'timestamp': tx_time, 'txhash': tx_hash})
    if i > 10:
        break
