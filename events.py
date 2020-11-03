import asyncio
from concurrent.futures import ProcessPoolExecutor

from sqlite3 import OperationalError, connect as connect_db

import time
from datetime import (
    datetime as dt,
    timedelta as td,
    timezone as tz)
from enum import Enum


class Intervals(Enum):
    hour = 1
    day = 24
    week = 24*7
    halfmounth = 24*7*2
    all = 2**24


class EventsReader:

    by_hour_query = """
    SELECT hour, count(*) as shifts
    FROM events
    WHERE type==1 AND hour BETWEEN {} AND {}
    GROUP BY hour
    """
    all_query = """
    SELECT hour+secs as time
    FROM events
    WHERE type==1 AND time BETWEEN {} AND {}
    """

    def __init__(self, dbname):
        self.dbname = dbname

    def ask_db(self, query, retries=5, delay=0.5):
        with connect_db(self.dbname) as conn:
            cursor = conn.cursor()
            for _ in range(retries):
                try:
                    response = cursor.execute(query).fetchall()
                except OperationalError as err:
                    last_error = err
                    time.sleep(delay)
                else:
                    break
            else:
                raise last_error
            cursor.close()
        return response

    def _format_template(self, template, end, interval):
        delta = td(hours=interval)
        start = end - delta
        return template.format(
            start.timestamp(),
            end.timestamp()
        )

    def get_by_hours(self, interval):
        hours = Intervals[interval].value
        now_time = dt.now(tz.utc)
        query = self._format_template(
            self.by_hour_query,
            now_time,
            hours
        )
        return self.ask_db(query)

    def get_all(self, interval):
        hours = Intervals[interval].value
        now_time = dt.now(tz.utc)
        query = self._format_template(
            self.all_query,
            now_time,
            hours
        )
        return self.ask_db(query)
