# -*- coding:utf-8 -*-

from flask_migrate import MigrateCommand,Migrate
from flask_script import Manager
from ihome import create_app
from config import DevelopmentConfig,ProductionConfig
# manager文件主要管理文件启动:config配置/app创建/路由实现都不需要关心

# 程序的启动是调试模式还是发布模式,通过传参实现
app,db = create_app(DevelopmentConfig)

manager = Manager(app)

Migrate(app,db)

manager.add_command('db',MigrateCommand)


if __name__ == '__main__':
    manager.run()
