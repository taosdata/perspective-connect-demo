#  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#  ┃ ██████ ██████ ██████       █      █      █      █      █ █▄  ▀███ █       ┃
#  ┃ ▄▄▄▄▄█ █▄▄▄▄▄ ▄▄▄▄▄█  ▀▀▀▀▀█▀▀▀▀▀ █ ▀▀▀▀▀█ ████████▌▐███ ███▄  ▀█ █ ▀▀▀▀▀ ┃
#  ┃ █▀▀▀▀▀ █▀▀▀▀▀ █▀██▀▀ ▄▄▄▄▄ █ ▄▄▄▄▄█ ▄▄▄▄▄█ ████████▌▐███ █████▄   █ ▄▄▄▄▄ ┃
#  ┃ █      ██████ █  ▀█▄       █ ██████      █      ███▌▐███ ███████▄ █       ┃
#  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
#  ┃ Copyright (c) 2017, the Perspective Authors.                              ┃
#  ┃ ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌ ┃
#  ┃ This file is part of the Perspective library, distributed under the terms ┃
#  ┃ of the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). ┃
#  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

import random
import logging
from datetime import date, datetime
from datetime import timezone as tz
from time import sleep
import json
import taosws


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main')

# =============================================================================
# TDengine connection parameters
# =============================================================================
TAOS_HOST = "192.168.1.95"                 # TDengine server host
TAOS_PORT = 6041                        # TDengine server port
TAOS_USER = "root"                      # TDengine username
TAOS_PASSWORD = "taosdata"              # TDengine password

TAOS_DATABASE = "power"                # TDengine database name
TAOS_TABLENAME = "meters"        # TDengine table name

# =============================================================================
# Data generation parameters
# =============================================================================
INTERVAL = 300                      # seconds. insert data every INTERVAL milliseconds
NUM_ROWS_PER_INTERVAL = 300         # number of rows to insert every INTERVAL seconds
SECURITIES = [
    "San Francisco", 
    "Los Angles", 
    "San Diego",
    "San Jose", 
    "Palo Alto", 
    "Campbell", 
    "Mountain View",
    "Sunnyvale", 
    "Santa Clara", 
    "Cupertino"
]
# CLIENTS = ["Homer", "Marge", "Bart", "Lisa", "Maggie", "Moe", "Lenny", "Carl", "Krusty"]


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that serializes datetime and date objects
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


# json.JSONEncoder.default = CustomJSONEncoder().default


def gen_data():
    """
    Generate random data
    """
    modifier = random.random() * random.randint(1, 50)
    return [{
        "ts": datetime.now(),
        "current": random.uniform(0, 75) + random.randint(0, 9) * modifier,
        "voltage": random.randint(200, 225),
        "phase": random.uniform(0, 105) + random.randint(1, 3) * modifier,
    } for _ in range(NUM_ROWS_PER_INTERVAL)]


def create_database(
        conn, 
        database_name: str = TAOS_DATABASE
        ) -> None:
    """
    Create a TDengine database. Drop the database if it already exists.
    """
    
    # create the database
    conn.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    conn.execute(f"USE {database_name}")
    logger.info(f"TDengine - Created database {database_name}")


def create_table(
        conn, 
        table_name: str = TAOS_TABLENAME
        ) -> None:
    """
    Create a TDengine table to store the data. Drop the table if it already exists.
    """
    # drop the table if it already exists
    conn.execute(f"DROP TABLE IF EXISTS {table_name}")
    # create the table
    sql = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (`ts` TIMESTAMP, `current` FLOAT, `voltage` INT, `phase` FLOAT) TAGS (`groupid` INT, `location` BINARY(16))
    """
    conn.execute(sql)
    logger.info(f"TDengine - Created table {table_name}")


def insert_data(
        conn, 
        progress_counter,
        table_name: str = TAOS_TABLENAME
        ) -> None:
    """
    Insert data into the TDengine table
    """
    records = gen_data()
    
    # prepare a parameterized SQL statement
    sql = f"INSERT INTO ? USING `{table_name}` (groupid, location) TAGS(?,?) VALUES (?,?,?,?)"
    # sql = f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    stmt = conn.statement()
    stmt.prepare(sql)
    tableNo = progress_counter % 10
    tbname = f"d_bind_{tableNo}"
    tags = [
        taosws.int_to_tag(tableNo),
        taosws.varchar_to_tag(SECURITIES[tableNo]),
    ]

    stmt.set_tbname_tags(tbname, tags)
    
    # prepare the columns into their respective lists
    timestamps = [int(record['ts'].timestamp() * 1000) for record in records]
    currents = [record['current'] for record in records]
    voltages = [record['voltage'] for record in records]
    phases = [record['phase'] for record in records]

    # bind the parameters and execute the statement
    stmt.bind_param([
        taosws.millis_timestamps_to_column(timestamps),
        taosws.floats_to_column(currents),
        taosws.ints_to_column(voltages),
        taosws.floats_to_column(phases),
        ]
    )
    # send the batch for insert
    stmt.add_batch()
    stmt.execute()
    logger.debug(f"TDengine - Wrote {len(records)} rows to table {table_name}")

def main():
    """
    Create a TDengine client, create the database and table, and insert data into the table
    """
    # create a tdengine websocket client
    conn = taosws.connect(host=TAOS_HOST, port=TAOS_PORT, user=TAOS_USER, password=TAOS_PASSWORD)

    # create the database and table
    create_database(conn, database_name=TAOS_DATABASE)
    create_table(conn, table_name=TAOS_TABLENAME)
    
    progress_counter = 0
    logger.info(f"Inserting data to TDengine @ interval={INTERVAL:d}ms...")
    try:
        while True:
            insert_data(conn, progress_counter, table_name=TAOS_TABLENAME)
            progress_counter += 1
            print('.', end='' if progress_counter % 80 else '\n', flush=True)
            sleep((INTERVAL / 1000.0))
    except KeyboardInterrupt:
        logger.info(f"Shutting down...")


if __name__ == "__main__":
    main()