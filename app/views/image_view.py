import logging
from sanic import  Blueprint, response
from sanic.response import json, text, html, redirect
import ujson
import datetime

from hashlib import md5
from random import Random, random
import os
import sys
from os.path import getsize
sys.path.append("..")
from config import FILE_STATIC_PATH

logger = logging.getLogger('image')
image_bp = Blueprint('image', url_prefix='image')

async def save_image(details, data):
    md5_obj = md5()
    md5_obj.update(('_'.join(details)).encode('utf-8'))
    path = details[0] + md5_obj.hexdigest() + "." +details[-1].split('.')[-1]
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

@image_bp.route('/post',methods=['POST'])
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
            path = await save_image([request.app.config.FILE_STATIC_PATH,str(article_id),str(author_id),image_name],image_data)
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

@image_bp.route('/get', methods=['GET'])
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
