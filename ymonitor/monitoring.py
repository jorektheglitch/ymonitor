#!/usr/bin/env python3
import json
from sqlite3 import connect
from socket import create_connection, error as sock_err
from time import sleep

from typing import Optional

from db.sqlite import DBWriter


state = {
    'coords': None,
    'yggdrasil_alive': False
}

request = {'request': 'getSelf'}


def ask_yggdrasil() -> Optional[dict]:
    """
    Sends request for node coords to Yggdrasil Admin API.

    Returns a dict with request if request successed, else returns None.
    """
    try:
        y = create_connection(('localhost', 9001))
        json.dump(request, y.makefile('w'))
        raw_response = json.load(y.makefile('r'))
    except sock_err:
        return None
    assert isinstance(raw_response, dict)
    return raw_response.get('response', {})


def extract_coords(api_response: dict) -> str:
    """
    Extract node coords from Yggdrasil Admin API's response.
    """
    self = api_response.get('self', {})
    for overview in self.values():
        return overview['coords'][1:-1]


def mainloop(dbname: str) -> None:
    """
    Mainloop of monitoring service.

    Connects to a db and polls Yggdraisl Admin API for coords shifts or 
    Yggrdasil service downtimes.
    """
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
