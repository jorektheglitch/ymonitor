#!/usr/bin/env python3
import asyncio
import argparse
import logging
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path
from sys import argv

from typing import Callable, Coroutine, Type

from aiohttp import web

from db.sqlite import DBReader
from utils.enums import Intervals


DB_NAME = 'events.db'
e_reader = DBReader(DB_NAME)
executor = ProcessPoolExecutor(16)


def cast_hadler(func: Callable, res_type: Type, *args) -> Coroutine:
    """
    Casts a handler for aiohttp from given func.

    Param res_type specifies a type of values that will returns from handler.
    """
    async def handler(request: web.Request) -> web.Response:
        loop = asyncio.get_event_loop()
        ask = partial(func, *args)
        try:
            result = await loop.run_in_executor(executor, ask)
        except Exception as e:
            logging.error(
                "Exception {} occured in {} due to {}".format(
                    e.__class__.__name__, func.__name__, e
                ))
            raise web.HTTPInternalServerError()
        else:
            return web.json_response(res_type(result))
    return handler


def init_loggers(access: bool, server: bool) -> None:
    """
    Initialise a aiohttp access and server loggers.

    Param access and server are booleans and means enable or not enable each
    type of loggers.
    """
    for name, wanted in zip(('access', 'server'), (access, server)):
        if wanted:
            log = logging.getLogger('aiohttp.{}'.format(name))
            log.level = logging.INFO
            log_filename = './logs/{}.log'.format(name)
            logger_handler = logging.FileHandler(log_filename)
            logger_handler.setLevel(logging.INFO)
            log.addHandler(logger_handler)


loop = asyncio.get_event_loop()
app = web.Application()

handlers = {
    'by_hour': (e_reader.get_by_hours, dict),
    'all': (e_reader.get_all, list)
}

for interval in Intervals:
    i_name: str = interval.name
    for grouping, (func, response_type) in handlers.items():
        path = '/api/{interval_name}/{grouping}'.format(
            interval_name=i_name,
            grouping=grouping
        )
        handler = cast_hadler(func, response_type, i_name)
        app.router.add_route('GET', path, handler)
static_dir = Path.cwd() / 'www'
app.router.add_static('/', static_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description='Webservice for Yggdrasil 0.4 coords monitor'
    )
    parser.add_argument(
        '--host', metavar='host', type=str,
        help='addres to bind webservice to',
        default='127.0.0.1', required=False
    )
    parser.add_argument(
        '--port', metavar='port', type=int,
        help='port to bind webservice to',
        default=8080, required=False
    )
    args = parser.parse_args()
    host = args.host
    port = args.port
    web.run_app(app, host=host, port=port)
