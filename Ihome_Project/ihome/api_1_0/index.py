# -*- coding:utf-8 -*-
# 导入蓝图对象
from . import api
from ihome import db

@api.route('/')
def hello_world():
    return 'Hello World!'