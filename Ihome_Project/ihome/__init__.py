# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
# from config import DevelopmentConfig

# 所有的flask扩展都可以延迟加载,先再函数外部定义,方便别的文件导入,延迟传入app来加载相关配置
db = SQLAlchemy()

def create_app(config_obj):
    app = Flask(__name__)

    app.config.from_object(config_obj)

    # 延迟加载
    db.init_app(app)

    # 开启csrf保护
    CSRFProtect(app)

    # 将导包语句放在这,用时再导包,解决循环导包问题
    from ihome.api_1_0 import api
    # 注册蓝图,可传参
    app.register_blueprint(api,url_prefix='/api/1.0')
    return app,db

#
# @app.route('/')
# def hello_world():
#     return 'Hello World!'