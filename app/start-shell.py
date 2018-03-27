#!/usr/bin/env python
# encoding: utf-8
import os, sys
sys.setrecursionlimit(99999)
sys.path.append(os.path.dirname(__file__))

from server import BaseConnection, Redis, MemCache
import asyncio
from config import DB_CONFIG

def main():
    loop = asyncio.get_event_loop()
    db = None
    async def before_start(loop,DB_CONFIG):
        db = await BaseConnection(loop=loop).init(DB_CONFIG=DB_CONFIG)
        return db

    async def start_redis():
        r = Redis()
        redis_connection = await r.get_redis_pool()
        return redis_connection

    memCache = MemCache()



    db = loop.run_until_complete(before_start(loop,DB_CONFIG))
    redis = loop.run_until_complete(start_redis())
    local_vars = locals()
    local_vars['db'] = db
    local_vars['loop'] = loop
    local_vars['redis'] = redis
    def set_mem(key,value):
        async def run(key,value):
            res= await memCache.set(key,value)
            return res
        res = loop.run_until_complete(run(key,value))
        return res

    def get_mem(key):
        async def run(key):
            res= await memCache.get(key)
            return res
        res = loop.run_until_complete(run(key))
        return res

    def set_redis(key,value):
        async def run(key,value):
            res= await redis.set(key,value)
            return res
        res = loop.run_until_complete(run(key,value))
        return res

    def get_redis(key):
        async def run(key):
            res = await redis.get(key)
            return res
        res = loop.run_until_complete(get_redis(key))
        return res

    def fetch(sql):
        async def run(sql):
            async with db as cur:
                res = await cur.fetch(sql)
                return res
        res = loop.run_until_complete(run(sql))
        return res

    local_vars['fetch'] = fetch
    try:
        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        ipshell = InteractiveShellEmbed()
        ipshell()
    except ImportError:
        import code
        pyshell = code.InteractiveConsole(locals=local_vars)
        pyshell.interact()

if __name__ == "__main__":
    main()
