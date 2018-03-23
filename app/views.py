#!/usr/bin/env python
# encoding: utf-8

import logging
from sanic import  Blueprint, response
from sanic.response import json, text, html, redirect
import ujson
import datetime

from hashlib import md5
from random import Random

logger = logging.getLogger('susnote')
note_bp = Blueprint('note', url_prefix='note')

def create_salt(length = 4):
    salt = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    len_chars = len(chars)-1
    random = Random()
    for i in range(length):
        salt += chars[random.randint(0, len_chars)]
    return salt

def create_md5(pwd,salt):
    md5_obj = md5()
    md5_obj.update((pwd + salt).encode('utf-8'))
    return md5_obj.hexdigest()

@note_bp.route('/test',methods=['GET'])
async def test(request):
    return html('ss')

@note_bp.route('/register',methods=['POST'])
async def register(request):
    data = {}
    try:
        data = ujson.loads(request.body)
    except:
        return json({'error':'unknow error'},status=400)

    if not(data.get('password') and len(data.get('password'))>5):
        return json({'error':'illegal password'},status=400)

    if not(data.get('username') and len(data.get('username'))>3):
        return json({'error':'illegal username'},status=400)

    sql = """select * from author where username='%s'"""%data.get('username')
    logger.info(sql)
    async with request.app.db.acquire() as cur:
        records = await cur.fetch(sql)
        if not records:
            sql = ""
            salt = create_salt()
            password = create_md5(data.get('password'),salt)
            sql = """insert into author (username,nickname,password,password_salt) values ('%s','%s','%s','%s')"""\
            %(data.get('username'),data.get('username'),password,salt)
            try:
                await cur.fetch(sql)
                logger.info(sql)
            except Exception as e:
                logger.error(e)
                return json({'error':'service error'},status=400)
        else:
            return json({'error':'illegal username'},status=400)
    await login(request)
    return json({'success':'success'},status=200)

@note_bp.route('/login',methods=['POST'])
async def login(request):
    data = {}
    try:
        data = ujson.loads(request.body)
    except:
        return json({'error':'illegal information'},status=400)

    sql = """select * from author where username='%s'"""%data.get('username')
    logger.info(sql)
    async with request.app.db.acquire() as cur:
        try:
            records = await cur.fetch(sql)
        except Exception as e:
            logger.error(e)
            return json({'error':'illegal information'},status=400)

        if records:
            salt = records[0]['password_salt']
            password = records[0]['password']
            if password == create_md5(data.get('password'),salt):
                request['session']['author_id'] = records[0]['id']
                return json({'success':'success'},status=200)
    return json({'error':'illegal information'},status=400)

@note_bp.route('/logout',methods=['GET'])
async def logout(request):
    response = json({'success':'success'},status=200)
    del response.cookies['session']
    return response

@note_bp.route('/articles',methods=['GET'])
async def articles(request):
    articles = []

    author_id = request['session']['author_id'] if request['session']['author_id'] else -1
    if author_id <0 :
        return json({'error':'illegal information'}, status=400)

    sql = """select * from article where author_id = '%s'""" % author_id
    async with request.app.db.acquire() as cur:
        try:
            records = await cur.fetch(sql)
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

@note_bp.route('/article',methods=['POST'])
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

@note_bp.route('/article',methods=['PUT'])
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
