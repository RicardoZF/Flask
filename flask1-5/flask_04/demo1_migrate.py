# -*- coding:utf-8 -*-
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager

app = Flask(__name__)
manager = Manager(app)
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@192.168.44.129:3306/flask02'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 第一个参数是Flask的实例,第二个参数是Sqlalchemy数据库实例
migrate = Migrate(app,db)

#manager是Flask-Script的实例，这条语句在flask-Script中添加一个db命令
manager.add_command('db',MigrateCommand)

# 定义模型类Role
class Role(db.Model):
    # 定义表名
    __tablename__ = 't_roles'
    # 定义列对象
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(32),unique=True)
    users = db.relationship('User',backref='role')

# 定义模型类User
class User(db.Model):
    # 表名
    __tablename__ = 't_users'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(32),unique=True)
    # 外键
    role_id = db.Column(db.Integer,db.ForeignKey('t_roles.id'))

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    manager.run()
    # app.run(debug=True)
