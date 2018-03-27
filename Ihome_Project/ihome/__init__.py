# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ihome.api_1_0 import api
# from config import DevelopmentConfig

def create_app(config_obj):
    app = Flask(__name__)

    app.config.from_object(config_obj)
    db = SQLAlchemy(app)

    # 注册蓝图,可传参
    app.register_blueprint(api,url_prefix='/api/1.0')
    return app,db

#
# @app.route('/')
# def hello_world():
#     return 'Hello World!'