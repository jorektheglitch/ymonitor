from sqlite3 import Connection, OperationalError
from sqlite3 import connect as connect_db

import time
from datetime import (
    datetime as dt,
    timedelta as td,
    timezone as tz)
from enum import Enum

from typing import List, Tuple


class Intervals(Enum):
    hour = 1
    day = 24
    week = 24*7
    halfmounth = 24*7*2
    all = 2**24


class DBWriter:

    init_db = """
    CREATE TABLE IF NOT EXISTS events (
        hour int32,
        secs int16,
        type int8,
        coords text)
    """
    write_shutdown = """
    INSERT INTO events
    VALUES (?, ?, 2, NULL)
    """
    write_coords_change = """
    INSERT INTO events
    VALUES (?, ?, 1, ?)
    """

    def __init__(self, db_name: str = None, connection: Connection = None):
        self.conn = connection or connect_db(db_name)
        self.cursor = self.conn.cursor()
        self.ygg_alive = False
        self.coords = None
        self.cursor.execute(self.init_db)
        self.conn.commit()

    def ygg_shutdown_handler(self):
        self.coords = None
        if self.ygg_alive:
            print('[{}] Ygg down'.format(dt.now()))
            self.ygg_alive = False
            hours, secs = divmod(dt.now(tz.utc).timestamp(), 3600)
            secs = int(secs)
            self.cursor.execute(self.write_shutdown, (hours*3600, secs))
            self.conn.commit()

    def coords_event_handler(self, coords: str):
        now = dt.now()
        if not self.ygg_alive:
            print('[{}] Ygg up'.format(now))
            self.ygg_alive = True
        if self.coords != coords:
            self.coords = coords
            print("[{}] Coords: [{}]".format(now, coords))
            hour, secs = divmod(dt.now(tz.utc).timestamp(), 3600)
            secs = int(secs)
            self.cursor.execute(
                self.write_coords_change,
                (hour*3600, secs, coords)
            )
            self.conn.commit()


class DBReader:

    by_hour_query = """
    SELECT hour, count(*) as shifts
    FROM events
    WHERE type==1 AND hour BETWEEN ? AND ?
    GROUP BY hour
    """
    all_query = """
    SELECT hour+secs as time
    FROM events
    WHERE type==1 AND time BETWEEN ? AND ?
    """

    def __init__(self, dbname):
        self.dbname = dbname

    def ask_db(
        self, query, params=(), retries=5, delay=0.5
    ) -> List[Tuple[str, str]]:
        with connect_db(self.dbname) as conn:
            cursor = conn.cursor()
            for _ in range(retries):
                try:
                    response = cursor.execute(query, params).fetchall()
                except OperationalError as err:
                    last_error = err
                    time.sleep(delay)
                else:
                    break
            else:
                raise last_error
            cursor.close()
        return response

    def _get_interval(self, interval: str):
        hours = Intervals[interval].value
        end = dt.now(tz.utc)
        delta = td(hours=hours)
        start = end - delta
        return start.timestamp(), end.timestamp()

    def get_by_hours(self, delta: str):
        interval = self._get_interval(delta)
        return self.ask_db(self.by_hour_query, interval)

    def get_all(self, delta: str):
        interval = self._get_interval(delta)
        return self.ask_db(self.all_query, interval)
