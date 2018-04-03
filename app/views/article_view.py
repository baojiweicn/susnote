#!/usr/bin/env python
# encoding: utf-8

import logging
from sanic import  Blueprint, response
from sanic.response import json, text, html, redirect
import ujson
import datetime
from html import escape, unescape

logger = logging.getLogger('article')
article_bp = Blueprint('article', url_prefix='article')

@article_bp.route('/get',methods=['GET'])
async def articles(request):
    args = request.args
    limit = args.get('limit',10)
    start = args.get('start',0)
    order = args.get('order','desc')
    article_id = int(args.get('id',-1))
    notebook_id = int(args.get('notebook_id',-1))
    articles = []

    author_id = request['session']['author_id'] if request['session']['author_id'] else -1
    if author_id <0 :
        return json({'error':'illegal information'}, status=400)

    sql = """select * from article where author_id = '%s' """ % author_id
    if article_id >0:
        sql = sql + """and article_id=%s """ % article_id
    if notebook_id >0:
        sql = sql + """and notebook_id=%s """ % notebook_id
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
            articles.append({
            "id":       record['id'],
            "title":    unescape(record['title']),
            "content":  unescape(record['content']),
            "source":   unescape(record['source']),
            "notebook_id": record['notebook_id'],
            "author_name": unescape(request["session"]["author_name"]),
            })
    return json(articles)

@article_bp.route('/post',methods=['POST'])
async def add_article(request):
    data = {}
    try:
        data = ujson.loads(request.body)
    except:
        return json({'error':'illegal information'},status=400)

    author_id = request['session']['author_id'] if request['session']['author_id'] else -1
    if author_id <0:
        return json({'error':'illegal information'}, status=400)
    print(data)
    sql = """insert into article (title,content,author_id,source,notebook_id) values ('%s','%s','%s','%s','%s')""" \
    %(escape(data.get('title','')), escape(data.get('content','')), author_id, escape(data.get('source','')), data.get('notebook_id'))
    async with request.app.db.acquire() as cur:
        try:
            await cur.fetch(sql)
            logger.info(sql)
        except Exception as e:
            logger.error(e)
            return json({'error':'service error'}, status=400)
    return json({'success':'success'},status=200)

@article_bp.route('/put',methods=['PUT'])
async def update_article(request):
    data = {}
    try:
        data = ujson.loads(request.body)
    except Exceotion as e:
        return json({'error':'illegal information'},status=400)

    author_id = request['session']['author_id'] if request['session']['author_id'] else -1
    if author_id <0:
        return json({'error':'illegal information'}, status=400)
    article_id = data.get("id") if data.get("id") else -1
    if int(article_id)<0:
        return json({'error':'illegal information'},status=400)

    sql = """update article set title='%s', content='%s', author_id='%s',source='%s',notebook_id='%s' where id=%s""" \
    %(escape(data.get('title','')),escape(data.get('content','')),author_id,escape(data.get('source','')),data.get('notebook_id'),article_id)

    async with request.app.db.acquire() as cur:
        try:
            await cur.fetch(sql)
            logger.info(sql)
        except Exception as e:
            logger.error(e)
            return json({'error':'service error'}, status=400)
    return json({'success':'success'},status=200)

@article_bp.route('/delete',methods=['DELETE'])
async def delete_article(request):
    data = {}
    try:
        data = ujson.loads(request.body)
    except:
        return json({'error':'illegal information'},status=400)

    author_id = request['session']['author_id'] if request['session']['author_id'] else -1
    if author_id <0:
        return json({'error':'illegal information'}, status=400)
    article_id = data.get("id") if data.get("id") else -1
    if article_id<0:
        return json({'error':'illegal information'},status=400)

    sql = """delete from article where author_id='%s' and id=%s"""%(author_id,article_id)

    async with request.app.db.acquire() as cur:
        try:
            await cur.fetch(sql)
            logger.info(sql)
        except Exception as e:
            logger.error(e)
            return json({'error':'service error'}, status=400)
    return json({'success':'success'},status=200)
