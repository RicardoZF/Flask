# -*- coding:utf-8 -*-
# 导入蓝图对象
from flask import session
import logging
from . import api
from ihome import db

@api.route('/')
def hello_world():
    session['name']='xiaobai'
    logging.debug("This is a debug log.")
    logging.info("This is a info log.")
    logging.warning("This is a warning log.")
    logging.error("This is a error log.")
    logging.critical("This is a critical log.")
    return 'Hello World!'