import time
import sqlite3
import os
import re
import psutil
from flask import Flask, jsonify, send_file, request, Response

INTERVAL = int(os.getenv("INTERVAL", 1))
DB = "/data/metrics.db"

os.makedirs("/data", exist_ok=True)

conn = sqlite3.connect(DB, check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS metrics (
    ts INTEGER,
    npu REAL,
    cpu REAL,
    mem REAL
)
""")

conn.commit()

app = Flask(__name__)


def read_npu():
    try:
        with open("/sys/kernel/debug/rknpu/load") as f:
            txt = f.read()
        m = re.search(r'\d+', txt)
        return int(m.group()) if m else None
    except:
        return None


def collector():

    while True:

        ts = int(time.time())

        npu = read_npu()
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent

        if npu is not None:

            conn.execute(
                "INSERT INTO metrics VALUES (?,?,?,?)",
                (ts, npu, cpu, mem)
            )

            # keep only 7 days
            conn.execute(
                "DELETE FROM metrics WHERE ts < strftime('%s','now') - 604800"
            )

            conn.commit()

        time.sleep(INTERVAL)


@app.route("/data")
def data():

    range_sec = int(request.args.get("range", 7200))
    now = int(time.time())
    start = now - range_sec

    rows = []

    # high resolution (last 2h)
    if range_sec <= 7200:

        cur = conn.execute(
            "SELECT ts,npu,cpu,mem FROM metrics WHERE ts > ? ORDER BY ts",
            (start,)
        )
        rows = cur.fetchall()

    # medium resolution (last 24h)
    elif range_sec <= 86400:

        cur = conn.execute("""
            SELECT (ts/10)*10,
                   avg(npu),
                   avg(cpu),
                   avg(mem)
            FROM metrics
            WHERE ts > ?
            GROUP BY ts/10
            ORDER BY ts
        """, (start,))
        rows = cur.fetchall()

    # long range (week)
    else:

        cur = conn.execute("""
            SELECT (ts/60)*60,
                   avg(npu),
                   avg(cpu),
                   avg(mem)
            FROM metrics
            WHERE ts > ?
            GROUP BY ts/60
            ORDER BY ts
        """, (start,))
        rows = cur.fetchall()

    return jsonify(rows)


@app.route("/export")
def export():

    cur = conn.execute("SELECT ts,npu,cpu,mem FROM metrics ORDER BY ts")

    def generate():
        yield "timestamp,npu,cpu,mem\n"
        for ts,npu,cpu,mem in cur:
            yield f"{ts},{npu},{cpu},{mem}\n"

    return Response(generate(), mimetype="text/csv")


@app.route("/")
def index():
    return send_file("index.html")


if __name__ == "__main__":

    import threading

    t = threading.Thread(target=collector)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=8080)
