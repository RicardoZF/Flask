# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from config import DevelopmentConfig

def create_app(config_obj):
    app = Flask(__name__)

    app.config.from_object(config_obj)
    db = SQLAlchemy(app)

    return app,db

#
# @app.route('/')
# def hello_world():
#     return 'Hello World!'