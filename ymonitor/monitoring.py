#!/usr/bin/env python3
from sqlite3 import connect, Cursor, OperationalError
from socket import create_connection, error as sock_err
import json
from time import sleep
from datetime import datetime as dt
from datetime import timezone as tz

from utils.db import DBWriter

state = {
    'coords': None,
    'yggdrasil_alive': False
}

request = {'request': 'getSelf'}

def ask_yggdrasil() -> dict:
    try:
        y = create_connection(('localhost', 9001))
        json.dump(request, y.makefile('w'))
        raw_response = json.load(y.makefile('r'))
        assert isinstance(raw_response, dict)
    except sock_err:
        return None
    return raw_response.get('response', {})

def extract_coords(api_response:dict) -> str:
    self = api_response.get('self', {})
    for overview in self.values():
        return overview['coords'][1:-1]

def mainloop(dbname:str):
    with connect(dbname) as db:
        writer = DBWriter(connection=db)
        while True:
            api_response = ask_yggdrasil()
            if not api_response:
                writer.ygg_shutdown_handler()
            else:
                now_coords = extract_coords(api_response)
                writer.coords_event_handler(now_coords)
            sleep(2)

if __name__ == "__main__":
    mainloop('events.db')
