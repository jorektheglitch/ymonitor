#!/usr/bin/env python3
from sqlite3 import connect, Cursor, OperationalError
from socket import create_connection, error as sock_err
import json
from time import sleep
from datetime import datetime as dt
from datetime import timezone as tz


state = {
    'coords': None,
    'yggdrasil_alive': False
}

request = {'request': 'getSelf'}

def make_request():
    try:
        y = create_connection(('localhost', 9001))
        json.dump(request, y.makefile('w'))
        raw_response = json.load(y.makefile('r'))
        assert isinstance(raw_response, dict)
    except sock_err:
        return None
    return raw_response.get('response', {})

def extract_coords(api_response):
    self = api_response.get('self', {})
    for overview in self.values():
        return overview['coords'][1:-1]

def create_events_table(cursor: Cursor): ...

def init_db(cursor: Cursor):
    events_table = cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            hour int32,
            secs int16,
            type int8,
            coords text)""")

def mark_ygg_shutdown(cursor: Cursor):
    if state['yggdrasil_alive']:
        print('[{}] Ygg down'.format(dt.now()))
        state['yggdrasil_alive'] = False
        time, secs = divmod(dt.now(tz.utc).timestamp(), 3600)
        secs = int(secs)
        cursor.execute("""
            INSERT INTO events
            VALUES (?, ?, 2, NULL)""", (time*3600, secs))

def coords_event_handler(cursor: Cursor, coords: str):
    now = dt.now()
    if not state['yggdrasil_alive']:
        print('[{}] Ygg up'.format(now))
        state['yggdrasil_alive'] = True
    print("[{}] Coords: [{}]".format(now, coords))
    time, secs = divmod(dt.now(tz.utc).timestamp(), 3600)
    secs = int(secs)
    cursor.execute("""
        INSERT INTO events
        VALUES (?, ?, 1, ?)""", (time*3600, secs, coords))

def mainloop(dbname):
    with connect(dbname) as db:
        c = db.cursor()
        init_db(c)
        while True:
            api_response = make_request()
            if not api_response:
                mark_ygg_shutdown(c)
                db.commit()
                state['coords'] = None
                sleep(2)
                continue
            now_coords = extract_coords(api_response)
            if now_coords != state['coords']:
                coords_event_handler(c, now_coords)
                db.commit()
                state['coords'] = now_coords
            sleep(2)

if __name__ == "__main__":
    mainloop('events.db')
