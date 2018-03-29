# -*- coding:utf-8 -*-
import redis
class Config(object):
    # 配置数据库
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 是app.secret_key的值,secret_key = ConfigAttribute('SECRET_KEY')
    # 利用 密码随机生成器 和 base64 解码得到随机字符串
    # import base64,os
    # base64.b64encode(os.urandom(24))   # 24位
    # Out[4]: 'Xhe7ITbhK6rRFfwfFqj/8r/5w41poMCC'
    SECRET_KEY = 'Xhe7ITbhK6rRFfwfFqj/8r/5w41poMCC'

    # 配置redis
    REDIS_HOST = '192.168.44.129'
    REDIS_PORT = 6379

    # 配置flask_session,并将其存到redis

    SESSION_TYPE = 'redis'  # 指定存储session的位置为redis
    SESSION_USE_SIGNER = True  # 对数据进行签名加密, 提高安全性
    PERMANENT_SESSION_LIFETIME = 86400  # 单位是秒, 设置session过期的时间
    #  设置redis的ip和端口, db 可设置 redis具体的库,host 默认是 localhost
    SESSION_REDIS = redis.StrictRedis(db=2,host=REDIS_HOST, port=REDIS_PORT)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    # 未来可覆盖
    # DATABASE_URI = 'mysql://user@localhost/foo'
    pass

# class TestingConfig(Config):
#     TESTING = True
