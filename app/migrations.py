#!/usr/bin/env python
# encoding: utf-8

import logging
from playhouse.migrate import *
from peewee import ProgrammingError

from config import DB_CONFIG
from models import *

logger = logging.getLogger('models_migration')

db = PostgresqlDatabase(**DB_CONFIG)
migrator = PostgresqlMigrator(db)
db.connect()

class MigrationModel(object):
    _db = db
    _migrator = migrator

    def __init__(self):
        if self._model:
            self._model.bind(self._db, bind_refs=False, bind_backrefs=False)
            dis = getattr(self._model._meta, 'distribute', None)
            if dis:
                qc = self._db.compiler()
                qt = list(qc.create_tables([self._model]))
                qt[0] += dis
                self._db.execute_sql(*tuple(qt))
            else:
                self._db.create_tables([self._model])
            self._name = self._model._meta.table_name

    def add_column(self, col, field=None):
        print('Migrating==> [%s] add_column: %s' % (self._name, col))
        field = getattr(self._model, col) if not field else field
        return self.migrator.add_column(self._name, col, field)

    def rename_column(self, old, new):
        print('Migrating==> [%s] rename_column: (%s)-->(%s)' % (self._name, old, new))
        return self.migrator.rename_column(self._name, old, new)

    def drop_column(self, col):
        print('Migrating==> [%s] drop_column: %s' % (self._name, col))
        return self.migrator.drop_column(self._name, col)

    def drop_not_null(self, col):
        print('Migrating==> [%s] drop_not_null: %s' % (self._name, col))
        return self.migrator.drop_not_null(self._name, col)

    def add_not_null(self, col):
        print('Migrating==> [%s] add_not_null: %s' % (self._name, col))
        return self.migrator.add_not_null(self._name, col)

    def rename_table(self, name):
        print('Migrating==> [%s] rename_table: %s' % (self._name, name))
        return self.migrator.rename_table(self._name, name)

    def add_index(self, cols, unique=False):
        print('Migrating==> [%s] add_index: %s' % (self._name, cols))
        return self.migrator.add_index(self._name, cols, unique)

    def drop_index(self, col):
        print('Migrating==> [%s] drop_index: %s' % (self._name, col))
        return self.migrator.drop_index(self._name, col)

class Article_Migration(MigrationModel):
	_model = Article
	_db = db
	_migrator = migrator

class Article_History_Migration(MigrationModel):
	_model = Article_History
	_db = db
	_migrator = migrator

class Author_Migration(MigrationModel):
	_model = Author
	_db = db
	_migrator = migrator

class Image_Migration(MigrationModel):
	_model = Image
	_db = db
	_migrator = migrator

class RSS_Source_Migration(MigrationModel):
	_model = RSS_Source
	_db = db
	_migrator = migrator

class RSS_Flow_Migration(MigrationModel):
	_model = RSS_Flow
	_db = db
	_migrator = migrator

class RSS_Category_Migration(MigrationModel):
	_model = RSS_Category
	_db = db
	_migrator = migrator

def migrations():
    article_Migration = Article_Migration()
    article_History_Migration = Article_History_Migration()
    author_Migration = Author_Migration()
    image_Migration = Image_Migration()
    rss_source_Migration = RSS_Source_Migration()
    rss_Flow_Migration = RSS_Flow_Migration()
    rss_Category_Migration = RSS_Category_Migration()

    try:
        with db.transaction():
            #rec.migrate_v1()
            print("Success Migration")
    except ProgrammingError as e:
        raise e
    except Exception as e:
        raise e

if __name__ == '__main__':
    migrations()

