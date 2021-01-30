from sqlite3 import OperationalError
from sqlite3 import connect as connect_db

import time
from datetime import (
    datetime as dt,
    timedelta as td,
    timezone as tz)

from typing import List, Tuple

from utils.enums import Intervals


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
