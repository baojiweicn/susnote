#!/usr/bin/env python
# encoding: utf-8

from configparser import ConfigParser

config_parser = ConfigParser()
config_parser.read("../config")

def config_get(section, option):
    detail = config_parser.get(section, option)
    if detail in ['Yes','Y','True','true']:
        detail = True
    elif detail in ['No','no','False','false']:
        detail = False
    elif detail in ['None','none','','null','Null']:
        detail = None
    try:
        detail = int(detail)
    except:
        pass
    return detail

DB_CONFIG = {
    'host': config_get('database', 'host'),
    'user': config_get('database', 'user'),
    'password': config_get('database', 'password'),
    'port': config_get('database', 'port'),
    'database': config_get('database','database')
}

REDIS_CONFIG = {
    'host': config_get('redis', 'host'),
    'port': config_get('redis', 'port'),
    'open': config_get('redis', 'open')
}

DEBUG = config_get('security','debug')
WORKERS = config_get('security', 'workers')
TEMPLATE_PATH = 'template/html'
