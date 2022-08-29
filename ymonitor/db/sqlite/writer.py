from datetime import (
    datetime as dt,
    timezone as tz
)
from sqlite3 import Connection, Cursor
from sqlite3 import connect as connect_db

from typing import Optional


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
        self.conn: Connection = connection or connect_db(db_name)
        self.cursor: Cursor = self.conn.cursor()
        self.ygg_alive: bool = False
        self.coords: Optional[str] = None
        self.cursor.execute(self.init_db)
        self.conn.commit()

    def ygg_shutdown_handler(self) -> None:
        self.coords = None
        if self.ygg_alive:
            print('[{}] Ygg down'.format(dt.now()))
            self.ygg_alive = False
            hours, secs = divmod(dt.now(tz.utc).timestamp(), 3600)
            secs = int(secs)
            self.cursor.execute(self.write_shutdown, (hours*3600, secs))
            self.conn.commit()

    def coords_event_handler(self, coords: str) -> None:
        now: dt = dt.now()
        if not self.ygg_alive:
            print('[{}] Ygg up'.format(now))
            self.ygg_alive = True
        if self.coords != coords:
            self.coords = coords
            coords_str = str(coords)
            print("[{}] Coords: {}".format(now, coords))
            hour, secs = divmod(dt.now(tz.utc).timestamp(), 3600)
            secs = int(secs)
            self.cursor.execute(
                self.write_coords_change,
                (hour*3600, secs, coords_str)
            )
            self.conn.commit()
