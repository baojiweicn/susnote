#!/usr/bin/env python
# encoding: utf-8

import logging
from sanic import  Blueprint, response
from sanic.response import json, text, html, redirect
import ujson
import datetime
from config import FILE_STATIC_PATH

from hashlib import md5
from random import Random, random
import os
from os.path import getsize

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

async def save_image(details, data):
    md5_obj = md5()
    md5_obj.update(('_'.join(details)).encode('utf-8'))
    path = FILE_STATIC_PATH + md5_obj.hexdigest() + "." +details[-1].split('.')[-1]
    try:
        fs = open(path, 'wb')
        fs.write(data)
        fs.close()
        logger.info("save %s image success"% str(details))
        return path
    except Exception as e:
        logger.error("save %s image fail"% str(details))
        logger.error(e)
        return None


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

@note_bp.route('/image',methods=['POST'])
async def post_image(request):
    try:
        form = request.form
        image = request.files.get("image")
        image_name = image.name
        image_type = image.type
        image_data = image.body
        article_id = form.get('article_id',-1)
        title = form.get('title','')
        related_id = form.get('related_id',-1)
        author_id = request['session']['author_id']
    except:
        return json({'error':'illegal information'},status=400)

    async with request.app.db.acquire() as cur:
        try:
            path = await save_image([str(article_id),str(author_id),image_name],image_data)
            if path:
                size = getsize(path)
                sql = "insert into image (path,title,article_id,size,related_id,author_id,type) \
                values ('%s','%s','%s','%s','%s','%s','%s')"%(path,title,article_id,size,related_id,author_id,image_type)
                await cur.fetch(sql)
                logger.info(sql)
        except Exception as e:
            logger.error(e)
            return json({'error':'service error'},status=400)
    return json({'success':'success'},status=200)

@note_bp.route('/image', methods=['GET'])
async def get_image(request):
    images = []
    try:
        args = request.args
        image_id = args.get("id",-1)
        image_title = args.get("title","")
        article_id = args.get("article_id",-1)
        author_id = request['session']['author_id']
        limit = args.get('limit',10)
        start = args.get('start',0)
        order = args.get('order','desc')
    except Exception as e:
        return json({'error':'illegal information'},status=400)

    async with request.app.db.acquire() as cur:
        sql = """select * from image where author_id=%s """%author_id
        if int(image_id) >0 :
            sql = sql + """and id=%s """%image_id
        if image_title !="":
            sql = sql + """and image_title=%s """%image_title
        if int(article_id) >0:
            sql = sql + """and article_id=%s """%article_id
        sql =  sql + """order by id %s limit %s offset %s""" % (order,limit,start)
        print(sql)
        try:
            records = await cur.fetch(sql)
            if records:
                for record in records:
                    images.append({
                    "id":       record['id'],
                    "title":    record['title'],
                    "path":  record['path'],
                    "article_id":   record['article_id'],
                    "size": record["size"],
                    "type": record["type"],
                    "related_id": record["related_id"]
                    })
            logger.info(sql)
        except Exception as e:
            logger.error(e)
            return json({'error':'illegal information'}, status=400)

        return json(images)
