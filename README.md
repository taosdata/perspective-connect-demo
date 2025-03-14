# TDengine <> Perspective Integration

[![TDengine - Perspective Integration](imgs/prsp-tdengine_short.gif)](https://www.loom.com/share/5aa9f1d435d6430c99efa02559d3cd6c?sid=54d0ffbe-1906-4513-ad05-1898c8cbbe2d)

This document explains how to configure Perspective with a TDengine data source. 

<br/>

The architecture is as follow:

1. Install TDengine python client libs (taospy).
1. Instantiate a TDengine docker container.
1. Start a producer script (`producer.py`) which simulates real-time data ingestion into TDengine.
1. Start a perspective-python server (`perspective_server.py`) which reads data periodically from TDengine and publishes it out to Perspective real-time Table via a Tornado Websocket.
1. Embed a Perspective viewer in HTML and connect to the backend Server.
1. Visualize and interact with TDengine data in real-time

<br/><br>

## Overview

This guide demonstrates how to integrate [TDengine](https://tdengine.com/), a high-performance time-series database, with [Perspective](https://perspective.finos.org/), a powerful data visualization library. By combining these technologies, you can create a real-time data visualization platform that streams data from TDengine to a web-based Perspective viewer.

![TDengine - Perspective Architecture](imgs/tdengine_prsp_architecture.jpg)

### Key Steps:

1. **Install and Configure TDengine client**: Set up the TDengine python client.
2. **Docker Setup**: Deploy a TDengine Docker container and populate it with benchmark data.
3. **Virtual Environment**: Create and configure a virtual environment with necessary Python dependencies.
4. **Data Producer**: Implement a script to simulate real-time data ingestion into TDengine.
5. **Perspective Server**: Develop a server to stream data from TDengine to a Perspective viewer.
6. **Perspective Viewer**: Embed and configure a Perspective viewer in an HTML page for data visualization.

By following these steps, you can create a scalable and efficient platform for real-time data analysis and monitoring. Customize and extend the provided examples to fit your specific use case, whether it's monitoring stock prices, IoT sensor data, or other time-series data.

We hope this guide has been helpful in getting you started with TDengine and Perspective. For further information and advanced features, please refer to the helpful resources provided. Happy coding!

### TDengine

[TDengine](https://tdengine.com/) is a high-performance, scalable time-series database designed specifically for handling large volumes of time-series data. It excels in scenarios requiring real-time data ingestion, storage, and analysis, making it an ideal choice for monitoring metrics in various industries such as IoT, finance, and telecommunications. TDengine's efficient data compression, high throughput, and low-latency query capabilities enable organizations to gain actionable insights from their time-series data, ensuring timely and informed decision-making.

### Perspective

Perspective is a powerful data visualization library that enables interactive, real-time data analysis in web applications. Developed by [Prospective.co](https://prospective.co), Perspective leverages WebAssembly and Web Workers to provide high-performance data visualization capabilities directly in the browser. With Perspective, you can create dynamic dashboards, charts, and tables that update in real-time, allowing users to explore and interact with data seamlessly. Perspective's flexibility, speed, and ease of use make it an excellent choice for building data-driven applications that require real-time data visualization and analysis.

<br/><br/>

## Getting Started

### 1. Install TDengine client

Run the `install.sh` script to download and install the TDengine client libraries locally. This is necessary for the TDengine Python SDK (taospy) to function.

For more information on installing TDengine's client, please refer to [install client library](https://docs.tdengine.com/tdengine-reference/client-libraries/#install-client-driver) docs.

```sh
./install.sh
```

### 2. Check the client installation

After the install script runs, please verify if the everything is setup correctly.

You should see a symlink for `libtaos.so` in:

```sh
ls -l tdengine-client/driver/
```

Output:

```txt
total 68488
lrwxrwxrwx 1 warthog warthog       18 Jan  7 16:08 libtaos.so -> libtaos.so.3.3.5.0
-rwxr-xr-x 1 warthog warthog 59186032 Dec 31 03:42 libtaos.so.3.3.5.0
-rwxr-xr-x 1 warthog warthog 10937480 Dec 31 03:42 libtaosws.so
-rw-r--r-- 1 warthog warthog        8 Dec 31 03:42 vercomp.txt
```

Check if the client lib folder is correctly added to `$LD_LIBRARY_PATH`:

```sh
echo $LD_LIBRARY_PATH
```

`LD_LIBRARY_PATH` should have been added to your bash profile file. Please check to ensure that it is set properly.

If you don't see this line at the end of your `~/.bashrc` or `~/.bash_profile`, please add it:

```sh
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:***YOUR PATH***/tdengine-client/driver"
```

### 3. Start a TDengine Docker container

Run the `docker.sh` script to start a TDengine container. This script will also wait for the database to initialize.

```sh
./docker.sh
```

If you with to pre-populate the TDengine container with benchmark data. Run the script with the following flag:

```sh
./docker --benchmark
```

For complete information on running TDengine docker engine, please refer to [Get Started with TDengine Using Docker](https://docs.tdengine.com/get-started/deploy-in-docker/) docs.

### 4. Activate your virtualenv

`install.sh` already sets up a virtual environment for you and installs the TDengine `taospy` client. If you need to activate it manually, use the following commands:

```sh
source venv/bin/activate

pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

### 4. Run the producer

Run the `producer.py` script to periodically insert data into TDengine. This script simulates real-time data ingestion by generating random data points and inserting them into the TDengine database.

```sh
python producer.py
```

### 5. Run Perspective Server

Run the `perspective_server.py` script to start a Perspective server (on a new terminal). This server will pull data from TDengine and stream it into a Tornado WebSocket.

```sh
python perspective_server.py
```

**NOTE:** Don't forget to activate your virtual environment before running the script.

### 6. Open the Perspective Viewer

Open the `prsp-viewer.html` file in your browser to view the Perspective Table. This table will display the real-time data streamed from TDengine.

```sh
open prsp-viewer.html
```

<br/><br/>

## Explained

### `docker.sh`

The `docker.sh` script starts a TDengine Docker container. It waits for the database to initialize before returning. You can run this script with the following flags:

- `--benchmark`: Pre-populates the TDengine container with benchmark data.
- `--no-pull`: Skips pulling the TDengine Docker image.

```sh
./docker.sh --benchmark --no-pull
```

<br/>

### `producer.py`

The `producer.py` script connects to the TDengine database and inserts data at regular intervals. 

Here's how it works:

1. **Connecting to TDengine:**

```python
import taosws

TAOS_HOST = "localhost"
TAOS_PORT = 6041
TAOS_USER = "root"
TAOS_PASSWORD = "taosdata"

conn = taosws.connect(host=TAOS_HOST, port=TAOS_PORT, user=TAOS_USER, password=TAOS_PASSWORD)
```

2. **Creating a table:**

```python
create_table = """
CREATE TABLE IF NOT EXISTS stocks_values (
    timestamp TIMESTAMP,
    ticker NCHAR(10),
    client NCHAR(10),
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume INT UNSIGNED,
    date TIMESTAMP
)
"""
conn.execute(create_table)
```

3. **Inserting data:**

The `gen_data()` method generates a series of random stock trades on every call:

```python
import random
from datetime import datetime, date, timezone as tz

def gen_data():
    modifier = random.random() * random.randint(1, 50)
    return [{
        "timestamp": datetime.now(tz=tz.utc),
        "ticker": random.choice(["AAPL.N", "AMZN.N", "QQQ.N", "NVDA.N", "TSLA.N", "FB.N", "MSFT.N", "TLT.N", "XIV.N", "YY.N", "CSCO.N", "GOOGL.N", "PCLN.N"]),
        "client": random.choice(["Homer", "Marge", "Bart", "Lisa", "Maggie", "Moe", "Lenny", "Carl", "Krusty"]),
        "open": random.uniform(0, 75) + random.randint(0, 9) * modifier,
        "high": random.uniform(0, 105) + random.randint(1, 3) * modifier,
        "low": random.uniform(0, 85) + random.randint(1, 3) * modifier,
        "close": random.uniform(0, 90) + random.randint(1, 3) * modifier,
        "volume": random.randint(10_000, 100_000),
        "date": date.today(),
    } for _ in range(250)]
```

The `insert_data()` method uses prepared statements and batch inserts to enhance performance. By generating a batch of records at a time and using a prepared SQL statement, the method minimizes the overhead associated with multiple individual insert operations. This approach ensures efficient data insertion into the TDengine database.

```python
def insert_data(conn):
    records = gen_data()
    sql = "INSERT INTO stocks_values VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    stmt = conn.statement()
    stmt.prepare(sql)
    timestamps = [int(record['timestamp'].timestamp() * 1000) for record in records]
    tickers = [record['ticker'] for record in records]
    clients = [record['client'] for record in records]
    opens = [record['open'] for record in records]
    highs = [record['high'] for record in records]
    lows = [record['low'] for record in records]
    closes = [record['close'] for record in records]
    volumes = [record['volume'] for record in records]
    dates = [int(datetime.combine(record['date'], datetime.min.time()).timestamp() * 1000) for record in records]
    stmt.bind_param([
        taosws.millis_timestamps_to_column(timestamps),
        taosws.nchar_to_column(tickers),
        taosws.nchar_to_column(clients),
        taosws.floats_to_column(opens),
        taosws.floats_to_column(highs),
        taosws.floats_to_column(lows),
        taosws.floats_to_column(closes),
        taosws.ints_to_column(volumes),
        taosws.millis_timestamps_to_column(dates),
    ])
    stmt.add_batch()
    stmt.execute()


while True:
    insert_data(conn)
    time.sleep(0.25)
```

### `perspective_server.py`

The `perspective_server.py` script starts a Perspective server that reads data from TDengine and streams it to a Perspective Table via a Tornado WebSocket.

Here's how it works:

1. **Connecting to TDengine:**

```python
import taosws

TAOS_HOST = "localhost"
TAOS_PORT = 6041
TAOS_USER = "root"
TAOS_PASSWORD = "taosdata"

conn = taosws.connect(host=TAOS_HOST, port=TAOS_PORT, user=TAOS_USER, password=TAOS_PASSWORD)
```

2. **Reading data from TDengine:**

The `read_tdengine()` function queries the TDengine database and retrieves the latest stock data:

```python
def read_tdengine(conn):
    sql = """
        SELECT `timestamp`, ticker, client, open, high, low, close, volume, date
        FROM stocks_values
        WHERE `timestamp` >= NOW() - 1s
        ORDER BY `timestamp` DESC
        LIMIT 1000
    """
    res = conn.query(sql)
    data = [
        {
            "timestamp": convert_ts(row[0]),
            "ticker": row[1],
            "client": row[2],
            "open": row[3],
            "high": row[4],
            "low": row[5],
            "close": row[6],
            "volume": row[7],
            "date": convert_ts(row[8]),
        }
        for row in res
    ]
    return data
```

3. **Updating Perspective Table:**

The `perspective_thread()` function creates a Perspective table and updates it with new data from TDengine every 250 milliseconds:

```python
def perspective_thread(perspective_server, tdengine_conn):
    client = perspective_server.new_local_client()
    schema = {
        "timestamp": datetime,
        "ticker": str,
        "client": str,
        "open": float,
        "high": float,
        "low": float,
        "close": float,
        "volume": int,
        "date": datetime,
    }
    table = client.table(schema, limit=1000, name="stock_values")
    
    def updater():
        data = read_tdengine(tdengine_conn)
        table.update(data)
    
    callback = tornado.ioloop.PeriodicCallback(callback=updater, callback_time=250)
    callback.start()
```

4. **Starting Tornado WebSocket Server:**

The `make_app()` function sets up a Tornado application with a WebSocket handler to serve the Perspective table:

```python
def make_app(perspective_server):
    return tornado.web.Application([
        (
            r"/websocket",
            perspective.handlers.tornado.PerspectiveTornadoHandler,
            {"perspective_server": perspective_server},
        ),
    ])
```

5. **Running the server:**

The main block initializes the Perspective server, TDengine connection, and starts the Tornado IOLoop:

```python
if __name__ == "__main__":
    perspective_server = perspective.Server()
    tdengine_conn = create_tdengine_connection()
    app = make_app(perspective_server)
    app.listen(8080, address='0.0.0.0')
    
    loop = tornado.ioloop.IOLoop.current()
    loop.call_later(0, perspective_thread, perspective_server, tdengine_conn)
    loop.start()
```

### `prsp-viewer.html`

The `prsp-viewer.html` file embeds a Perspective Table in an HTML page. It connects to the Perspective server via a WebSocket and displays the real-time data streamed from TDengine.

Here's how it works:

1. **HTML Component:**

The HTML file includes the necessary Perspective libraries and sets up a `<perspective-viewer>` element within a container. This custom HTML component, written in WebAssembly, provides easily embeddable and highly interactive real-time data visualization on top of TDengine data. The viewer is configured to connect to the Perspective server via WebSocket and load the `stock_values` table, allowing for dynamic data visualization.

2. **Styling:**

CSS styles are applied to ensure the viewer occupies the full viewport and has a dark background.

3. **JavaScript Initialization:**

A script is included to load the Perspective viewer and connect it to the Perspective server via WebSocket. The viewer is bound to the `stock_values` table on the server, allowing real-time data updates to be displayed.

```html
<script type="module">
    import perspective from "https://cdn.jsdelivr.net/npm/@finos/perspective@3.1.3/dist/cdn/perspective.js";

    document.addEventListener("DOMContentLoaded", function() {
        async function load_viewer() {
            const table_name = "stock_values";
            const viewer = document.getElementById("prsp-viewer");
            const websocket = await perspective.websocket("ws://localhost:8080/websocket");
            const server_table = await websocket.open_table(table_name);
            await viewer.load(server_table);
        }
        load_viewer();
    });
</script>
```

4. **Viewer Configuration:**

The `perspective-viewer` element is configured with the "Pro Dark" theme to match the dark background and provide a consistent visual appearance.

<br/><br/>

## Conclusion

In this guide, we have walked through the process of integrating TDengine with Perspective to create a real-time data visualization platform. By following the steps outlined, you have learned how to:

1. Install and configure the TDengine client and server.
2. Set up a Docker container for TDengine and populate it with benchmark data.
3. Create a virtual environment and install necessary Python dependencies.
4. Implement a data producer to simulate real-time data ingestion into TDengine.
5. Develop a Perspective server to stream data from TDengine to a web-based Perspective viewer.
6. Embed and configure a Perspective viewer in an HTML page to visualize the data.

This integration allows you to leverage the high-performance time-series database capabilities of TDengine with the powerful data visualization features of Perspective. The combination of these technologies provides a robust solution for real-time data analysis and monitoring.

By following the provided examples and scripts, you can customize and extend this setup to fit your specific use case. Whether you are monitoring stock prices, IoT sensor data, or any other time-series data, this integration offers a scalable and efficient way to visualize and interact with your data in real-time.

We hope this guide has been helpful in getting you started with TDengine and Perspective. For further information and advanced features, please refer to the helpful resources provided. Happy coding!

<br/><br/>

## Helpful Resources

- **TDengine client library examples including python and node.js:** Download [TDengine's client library](https://docs.tdengine.com/tdengine-reference/client-libraries/#install-client-driver) tar file and unpack it. Look inside the examples directory for a comprehensive list of examples.

- [TDengine Docker Container with Data](https://docs.tdengine.com/get-started/deploy-in-docker/)
- [TDengine SQL Reference](https://docs.tdengine.com/basic-features/data-querying/)
- [Inserting data into TDengine](https://docs.tdengine.com/basic-features/data-ingestion/)

Next steps:
- [Streaming data from TDengine](https://docs.tdengine.com/advanced-features/stream-processing/)
