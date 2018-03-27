#!/usr/bin/env python
# encoding: utf-8

import logging
from asyncpg import connect, create_pool
from aiohttp import ClientSession

logger_db = logging.getLogger('susnote_db')

#create a connection with database
class BaseConnection(object):
    PGHOST = None
    PGUSER = None
    PGPASSWORD = None
    PGPORT = None
    PGDATABASE = None
    pool = None

    def __init__(self, loop=None):
        self.cursor = None
        self._loop = loop

    @property
    def rowcount(self):
        return self.cursor.rowcount

    async def create_connection(self):
        self.cursor = await self._pool.acquire()
        return self

    def acquire(self):
        return self._pool.acquire()

    async def init(self, DB_CONFIG):
        self._pool = await create_pool(**DB_CONFIG, loop=self._loop, max_size=100)
        return self

    async def add_listener(self, channel, callback):
        await self.cursor.add_listener(channel, callback)

    async def remove_listener(self, channel, callback):
        await self.cursor.remove_listener(channel, callback)

    async def execute(self, query:str, *args, timeout:float=None):
        return await self.cursor.execute(query, *args, timeout=timeout)

    async def executemany(self, command:str, args, timeout:float=None):
        return await self.cursor.executemmay(command, args, timeout=timeout)

    async def fetch(self, query, *args, timeout=None):
        return await self.cursor.fetch(query, *args, timeout=timeout)

    async def fetchrow(self, query, *args, timeout=None):
        return await self.cursor.fetchrow(query, *args, timeout=timeout)

    async def fetchval(self, query, *args, column=0, timeout=None):
        return await self.cursor.fetchval(query, *args, column=column, timeout=timeout)

    async def prepare(self, query, *args, timeout=None):
        return await self.cursor.prepare(query, *args, timeout=None)

    async def set_builtin_type_codec(self, typename, *args, schema='public', codec_name):
        await self.cursor.set_builtin_type_codec(typename, *args, schema=schema, codec_name=codec_name)

    async def set_type_codec(self, typename, *args, schema='public', encoder, decoder, binary=False):
        await self.cursor.set_type_codec(typename, *args, schema=schema, encoder=encoder, decoder=decoder, binary=binary)

    def transaction(self, *args, isolation='read_committed', readonly=False, deferrable=False):
        return self.cursor.transaction(*args, isolation=isolation, readonly=readonly, deferrable=deferrable)

    async def close(self):
        await self.cursor.close()

    async def release(self):
        await self._pool.release(self.cursor)

    async def closeAll(self):
        await self._pool.close()

    async def __aenter__(self):
        await self.create_connection()
        self.tr = self.transaction()
        await self.tr.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None:
                await self.tr.commit()
            else:
                await self.tr.rollback()
        except:
            pass
        finally:
            await self.release()

#create a client
class Client:
    _client = None

    def __init__(self, loop, url=None):
        self._client = ClientSession(loop=loop)
        self._url = url

    @property
    def cli(self):
        return self._client

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    def handler_url(self, url):
        if url.startswith("http"):
            return url
        if self._url:
            return "{}{}".format(self._url, url)
        return url

    def request(self, method, url, *args, **kwargs):
        return self._client.request(method, self.handler_url(url), *args, **kwargs)

    def get(self, url, allow_redirects=True, **kwargs):
        return self._client.get(self.handler_url(url), allow_redirects=True, **kwargs)

    def post(self, url, data=None, **kwargs):
        return self._client.post(self.handler_url(url), data=data, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self._client.put(self.handler_url(url), data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self._client.delete(self.handler_url(url), **kwargs)

    def head(self, url, allow_redirects=False, **kwargs):
        return self._client.head(self.handler_url(url), allow_redirects=allow_redirects, **kwargs)

    def options(self, url, allow_redirects=True, **kwargs):
        return self._client.options(self.handler_url(url), allow_redirects=allow_redirects, **kwargs)

    def close(self):
        self._client.close()

from sanic import Sanic
from sanic.response import json, text
from config import DEBUG, WORKERS, DB_CONFIG, REDIS_CONFIG, TEMPLATE_PATH, FILE_STATIC_PATH
from jinja2 import Environment, FileSystemLoader
import asyncio_redis

from sanic_session import RedisSessionInterface, InMemorySessionInterface

logger_main = logging.getLogger('susnote')
app = Sanic(__name__)

# create redis pool
class Redis:
    """
    A simple wrapper class that allows you to share a connection
    pool across your application.
    """
    _pool = None

    async def get_redis_pool(self):
        if not self._pool:
            self._pool = await asyncio_redis.Pool.create(host=REDIS_CONFIG['host'], port=REDIS_CONFIG['port'], poolsize=10)
        return self._pool

class MemCache(dict):
    def __init__(self):
        super(MemCache,self).__init__()

    async def set(self,key,value):
        self.update({key:value})

    async def get(self,key):
        return self[key]

    async def delete(self,key):
        try:
            del self[key]
        except Exception as e:
            return None

if REDIS_CONFIG['open']:
    redis = Redis()
    session_interface = RedisSessionInterface(redis.get_redis_pool)
else:
    memCache = MemCache()
    session_interface = InMemorySessionInterface()

@app.listener('before_server_start')
async def before_srver_start(app, loop):
    app.db = await BaseConnection(loop=loop).init(DB_CONFIG=DB_CONFIG)
    app.client =  Client(loop=loop)
    app.env = Environment(loader=FileSystemLoader(TEMPLATE_PATH), enable_async=True)
    if REDIS_CONFIG['open']:
        app.cache = await redis.get_redis_pool()
    else:
        app.cache = memCache

@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    app.client.close()

@app.middleware('request')
async def cros(request):
    if session_interface:
        await session_interface.open(request)
    if request.method == 'OPTIONS':
        headers = {'Access-Control-Allow-Origin': '*',
                   'Access-Control-Allow-Headers': 'Content-Type',
                   'Access-Control-Allow-Method': 'POST, PUT, DELETE'}
        return json({'message': 'Hello World'}, headers=headers)

@app.middleware('response')
async def cors_res(request, response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Method"] = "POST, PUT, DELETE"
    if session_interface:
        await session_interface.save(request, response)

from views import article_bp, image_bp, user_bp, notebook_bp
app.config.FILE_STATIC_PATH = FILE_STATIC_PATH
app.static('/','../frontend/')
app.blueprint(article_bp)
app.blueprint(image_bp)
app.blueprint(user_bp)
app.blueprint(notebook_bp)

@app.route("/")
async def test(request):
    return text('Hello world!')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=DEBUG)
