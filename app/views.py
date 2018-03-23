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
    len_chars = len(chars) -1
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
            %(data.get('username'),data.get('username'),data.get('password'),salt)
            try:
                await cur.fetch(sql)
                logger.info(sql)
            except Exception as e:
                logger.error(e)
                return json({'error':'service error'},status=400)
        else:
            return json({'error':'illegal username'},status=400)

    return json({'success':'success'},status=200)
