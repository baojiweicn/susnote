#!/usr/bin/env python
# encoding: utf-8

import logging
from sanic import  Blueprint, response
from sanic.response import json, text, html, redirect
import ujson
import datetime

logger = logging.getLogger('article')
article_bp = Blueprint('article', url_prefix='article')

@article_bp.route('/',methods=['GET'])
async def articles(request):
    args = request.args
    limit = args.get('limit',10)
    start = args.get('start',0)
    order = args.get('order','desc')
    article_id = args.get('id',-1)
    articles = []

    author_id = request['session']['author_id'] if request['session']['author_id'] else -1
    if author_id <0 :
        return json({'error':'illegal information'}, status=400)

    sql = """select * from article where author_id = '%s' """ % author_id
    if article_id >0:
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
            articles.append({
            "id":       record['id'],
            "title":    record['title'],
            "content":  record['content'],
            "source":   record['source']
            })
    return json(articles)

@article_bp.route('/',methods=['POST'])
async def add_article(request):
    data = {}
    try:
        data = ujson.loads(request.body)
    except:
        return json({'error':'illegal information'},status=400)

    author_id = request['session']['author_id'] if request['session']['author_id'] else -1
    if author_id <0:
        return json({'error':'illegal information'}, status=400)

    sql = """insert into article (title,content,author_id,source) values ('%s','%s','%s','%s')""" \
    %(data.get('title'), data.get('content'), author_id, data.get('source'))
    async with request.app.db.acquire() as cur:
        try:
            await cur.fetch(sql)
            logger.info(sql)
        except Exception as e:
            logger.error(e)
            return json({'error':'service error'}, status=400)
    return json({'success':'success'},status=200)

@article_bp.route('/',methods=['PUT'])
async def update_article(request):
    data = {}
    try:
        data = ujson.loads(request.body)
    except:
        return json({'error':'illegal information'},status=400)

    author_id = request['session']['author_id'] if request['session']['author_id'] else -1
    if author_id <0:
        return json({'error':'illegal information'}, status=400)
    article_id = data.get("article_id") if data.get("article_id") else -1
    if article_id<0:
        return json({'error':'illegal information'},status=400)

    sql = """update article set title='%s', content='%s', author_id='%s',source='%s' where id=%s""" \
    %(data.get('title'),data.get('content'),author_id,data.get('source'),article_id)

    async with request.app.db.acquire() as cur:
        try:
            await cur.fetch(sql)
            logger.info(sql)
        except Exception as e:
            logger.error(e)
            return json({'error':'service error'}, status=400)
    return json({'success':'success'},status=200)
