# -*- coding:utf-8 -*-
class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1/ihome06'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    # 未来可覆盖
    # DATABASE_URI = 'mysql://user@localhost/foo'
    pass

# class TestingConfig(Config):
#     TESTING = True
