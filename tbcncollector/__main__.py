""" TermoBeacon Collector daemon """

import asyncio
from sys import argv
from sqlite3 import connect
from struct import unpack
from time import time

from bleak import BleakScanner

db = None
INIT = (
    "create table if not exists autoinc(num int)",
    "insert into autoinc(num) select 0 where not exists"
        " (select 1 from autoinc)",
    "create table if not exists data(dt int, id int, addr text, batt float,"
        " temp float, humid float, tminc int, rssi int, primary key(dt, id))"
        " without rowid",
    "create temp trigger before insert on data begin"
        " update autoinc set num=num+1;"
        " end",
)
lastcommit = 0.0

def detection_callback(dev, data):
    global lastcommit
    # print("address", dev.address, "name", dev.name, "rssi", data.rssi)
    if dev.address.startswith("A3:E4:"):
        for k, v in data.manufacturer_data.items():
            if len(v) == 18:
                b, t, h, x, y, z = unpack("HHHBBB", v[8:17])
                tm = (z<<16) + (y<<8) + x
                dic = {"addr": dev.address,
                       "batt": b/1000,
                       "temp": t/16,
                       "humid": h/16,
                       "time": tm,
                       "rssi": data.rssi,
                }
                # bat 2.3 is empty, 3.1 is full
                # print(dic)
                db.execute("""\
                    insert into data (dt, id, addr, batt, temp, humid, tminc)
                    values (unixepoch(), (select num from autoinc),
                            :addr, :batt, :temp, :humid, :time)""",
                    dic)
                now = time()
                if now - lastcommit > 10.0:
                    db.commit()
                    lastcommit = now

async def main():
    async with BleakScanner(detection_callback=detection_callback):
        await asyncio.Future()

async def shutdown():
    db.commit()
    db.close()
    print("Shutdown complete")

if __name__ == "__main__":
    dbname = argv[1] if len(argv) == 2 else "/var/lib/tbcncollector/raw.db"
    db = connect(dbname)
    for cmd in INIT:
        db.execute(cmd)
    lastcommit = time()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(shutdown())
