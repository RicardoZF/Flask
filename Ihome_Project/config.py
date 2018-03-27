# -*- coding:utf-8 -*-
class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1/ihome06'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 是app.secret_key的值,secret_key = ConfigAttribute('SECRET_KEY')
    # 利用 密码随机生成器 和 base64 解码得到随机字符串
    # import base64,os
    # base64.b64encode(os.urandom(24))   # 24位
    # Out[4]: 'Xhe7ITbhK6rRFfwfFqj/8r/5w41poMCC'

    SECRET_KEY = 'Xhe7ITbhK6rRFfwfFqj/8r/5w41poMCC'

class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    # 未来可覆盖
    # DATABASE_URI = 'mysql://user@localhost/foo'
    pass

# class TestingConfig(Config):
#     TESTING = True
