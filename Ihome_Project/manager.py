# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import MigrateCommand,Migrate
from flask_script import Manager
app = Flask(__name__)

#  配置,迁移数据库
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:mysql@127.0.0.1/ihome06'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
manager = Manager(app)
db = SQLAlchemy(app)

Migrate(app,db)

manager.add_command('db',MigrateCommand)

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    manager.run()
