# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import MigrateCommand,Migrate
from flask_script import Manager
from config import DevelopmentConfig

app = Flask(__name__)

#  配置,迁移数据库
app.config.from_object(DevelopmentConfig)

manager = Manager(app)
db = SQLAlchemy(app)

Migrate(app,db)

manager.add_command('db',MigrateCommand)

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    manager.run()
