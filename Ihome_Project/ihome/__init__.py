# -*- coding:utf-8 -*-
from logging.handlers import RotatingFileHandler
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import redis
from config import Config
from flask_session import Session

# 所有的flask扩展都可以延迟加载,先再函数外部定义,方便别的文件导入,延迟传入app来加载相关配置
db = SQLAlchemy()
redis_store = None

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)

def create_app(config_obj):
    app = Flask(__name__)

    app.config.from_object(config_obj)

    # 延迟加载
    db.init_app(app)

    # 开启csrf保护
    CSRFProtect(app)

    # 创建redis
    global redis_store
    redis_store =  redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

    # 创建Session, 将session数据从以前默认的cookie, 存放到redis中
    Session(app)

    # 将导包语句放在这,用时再导包,解决循环导包问题
    from ihome.api_1_0 import api
    # 注册蓝图,可传参
    app.register_blueprint(api,url_prefix='/api/1.0')
    return app,db

#
# @app.route('/')
# def hello_world():
#     return 'Hello World!'