#!/usr/bin/env python
# encoding: utf-8

import logging
from sanic import  Blueprint, response
from sanic.response import json, text, html, redirect
import ujson
import datetime

logger = logging.getLogger('notebook')
notebook_bp = Blueprint('notebook', url_prefix='notebook')

@notebook_bp.route('/get',methods=['GET'])
async def notebooks(request):
    args = request.args
    limit = args.get('limit',10)
    start = args.get('start',0)
    order = args.get('order','desc')
    notebook_id = args.get('id',-1)

    notebooks = []

    author_id = request['session']['author_id'] if request['session']['author_id'] else -1

    if author_id <0 :
        return json({'error':'illegal information'}, status=400)

    sql = """select * from notebook where author_id = '%s' """ % author_id
    if notebook_id >0:
        sql = sql + """and article_id=%s """ % article_id
    sql = sql + """order by id %s limit %s offset %s""" % (order,limit,start)

    async with request.app.db.acquire() as cur:
        try:
            records = await cur.fetch(sql)
            logger.info(sql)
        except Exception as e:
            logger.error(e)
            return json({'error':'illegal information'}, status=400)

    if records:
        for record in records:
            notebooks.append({
            "id":       record['id'],
            "name":    record['name'],
            })
    return json(notebooks)

@notebook_bp.route('/post',methods=['POST'])
async def add_notebooks(request):
    data = {}
    try:
        data = ujson.loads(request.body)
    except:
        return json({'error':'illegal information'},status=400)

    author_id = request['session']['author_id'] if request['session']['author_id'] else -1
    if author_id <0:
        return json({'error':'illegal information'}, status=400)

    sql = """insert into notebook (name,author_id) values ('%s','%s')""" \
    %(data.get('name'), author_id)
    async with request.app.db.acquire() as cur:
        try:
            await cur.fetch(sql)
            logger.info(sql)
        except Exception as e:
            logger.error(e)
            return json({'error':'service error'}, status=400)
    return json({'success':'success'},status=200)

@notebook_bp.route('/put',methods=['PUT'])
async def update_notebook(request):
    data = {}
    try:
        data = ujson.loads(request.body)
    except:
        return json({'error':'illegal information'},status=400)

    author_id = request['session']['author_id'] if request['session']['author_id'] else -1
    if author_id <0:
        return json({'error':'illegal information'}, status=400)
    notebook_id = data.get("id") if data.get("id") else -1
    if article_id<0:
        return json({'error':'illegal information'},status=400)

    sql = """update notebook set name='%s', author_id='%s' where id=%s""" \
    %(data.get('name'),author_id,notebook_id)

    async with request.app.db.acquire() as cur:
        try:
            await cur.fetch(sql)
            logger.info(sql)
        except Exception as e:
            logger.error(e)
            return json({'error':'service error'}, status=400)
    return json({'success':'success'},status=200)

@notebook_bp.route('/delete',methods=['DELETE'])
async def delete_notebook(request):
    data = {}
    try:
        data = ujson.loads(request.body)
    except:
        return json({'error':'illegal information'},status=400)

    author_id = request['session']['author_id'] if request['session']['author_id'] else -1
    if author_id <0:
        return json({'error':'illegal information'}, status=400)
    notebook_id = data.get("id") if data.get("id") else -1
    if article_id<0:
        return json({'error':'illegal information'},status=400)

    sql = """delete from notebook where author_id='%s' and id=%s"""%(author_id,notebook_id)

    async with request.app.db.acquire() as cur:
        try:
            await cur.fetch(sql)
            logger.info(sql)
        except Exception as e:
            logger.error(e)
            return json({'error':'service error'}, status=400)
    return json({'success':'success'},status=200)
