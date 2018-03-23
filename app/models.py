#!/usr/bin/env python
# encoding: utf-8

from peewee import *
from playhouse.postgres_ext import *
import datetime

class BaseModel(Model):
	id = PrimaryKeyField()
	create_time = DateTimeField(verbose_name='create_time', constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

class Article(BaseModel):
	title = CharField(max_length=128)
	content = TextField(verbose_name='content')
	author_id = IntegerField(default='0')
	source = CharField(max_length=128)

	class Meta:ß
		db_table = 'article'

class Article_History(BaseModel):
	title = CharField(max_length=128)
	content = TextField(verbose_name='content')
	author_id = IntegerField(default='0')
	article_id = IntegerField(default='0')

	class Meta:
		db_table = 'article_history'

class Author(BaseModel):
	nickname = CharField(max_length=128)
	password = CharField(max_length=128)
	password_salt = CharField(max_length=128)
	username = CharField(max_length=128)

	class Meta:
		db_table = 'author'

class Image(BaseModel):
	path = CharField(max_length=128)
	title = CharField(max_length=128)
	article_id = IntegerField(default='0')
	size = CharField(max_length=128)
	related_id = IntegerField(default='0')

	class Meta:
		db_table = 'image'

class RSS_Source(BaseModel):
	url = CharField(max_length=128)
	title = CharField(max_length=128)
	update_time = DateTimeField(verbose_name='create_time', default=datetime.datetime.now)
	rss_category_id = IntegerField(default=0)

	class Meta:
		db_table = 'rss_source'

class RSS_Flow(BaseModel):
	url = CharField(max_length=128)
	title = CharField(max_length=128)
	author = CharField(max_length=128)
	is_readed = BooleanField(default=False)
	content = TextField(verbose_name='content')
	source_id = IntegerField(default='0')

	class Meta:
		db_table = 'rss_flow'

class RSS_Category(BaseModel):
	title = CharField(max_length=128)

	class Meta:
		db_table = 'rss_category'
