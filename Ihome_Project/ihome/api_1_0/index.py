# -*- coding:utf-8 -*-
# 导入蓝图对象
from flask import session

from . import api
from ihome import db

@api.route('/')
def hello_world():
    session['name']='xiaobai'
    return 'Hello World!'