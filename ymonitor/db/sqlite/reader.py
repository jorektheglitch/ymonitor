import time
from datetime import (
    datetime as dt,
    timedelta as td,
    timezone as tz)
from sqlite3 import Cursor, OperationalError
from sqlite3 import connect as connect_db

from typing import Iterable, List, Tuple
from typing import Optional, Union

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

    def __init__(self, dbname: str):
        self.dbname: str = dbname

    def ask_db(
        self, query: str, params: Optional[Iterable] = (),
        retries: Optional[int] = 5, delay: Optional[Union[int, float]] = 0.5
    ) -> List[Tuple[str, str]]:
        """
        Tries to execute given query with params several times (5 by default)
        with given delay (0.5 sec by default). Raises last catched exception if
        all of attempts failed.
        """
        with connect_db(self.dbname) as conn:
            cursor: Cursor = conn.cursor()
            for _ in range(retries):
                try:
                    response: Cursor = cursor.execute(query, params)
                    response: List[tuple] = response.fetchall()
                except OperationalError as err:
                    last_error: Exception = err
                    time.sleep(delay)
                else:
                    break
            else:
                raise last_error
            cursor.close()
        return response

    def _get_interval(self, interval: str) -> Tuple[int, int]:
        """
        Gets a tuple of two ints which is timestamps of moment in past and now.

        Moment in past defined by interval param.
        """
        hours: int = Intervals[interval].value
        end: dt = dt.now(tz.utc)
        delta: td = td(hours=hours)
        start: dt = end - delta
        return start.timestamp(), end.timestamp()

    def get_by_hours(self, delta: str) -> List[Tuple[str, str]]:
        """
        Gets a list of rows from DB. Each row is tuple of strings, which first
        string is timestamp of hour's start and second string is a number of
        coords shifts, that happens in this hour.
        """
        interval: Tuple[int] = self._get_interval(delta)
        return self.ask_db(self.by_hour_query, interval)

    def get_all(self, delta: str) -> List[Tuple[str]]:
        """
        Gets a list of rows from DB. Each row is tuple with one string that is
        timestamp of one coords change.
        """
        interval: Tuple[int] = self._get_interval(delta)
        return self.ask_db(self.all_query, interval)
