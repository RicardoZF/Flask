# -*- coding:utf-8 -*-
from flask import Blueprint

# 定义蓝图对象
api = Blueprint('api',__name__)

# 导入子模块
import index,verify_code,passport
