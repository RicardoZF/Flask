# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 设置连接数据库的url
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:mysql@127.0.0.1:3306/flask01'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 实例化数据库对象
db = SQLAlchemy(app)

class Role(db.Model):
    # 定义表名,不写,默认是模型类小写
    __tablename__ = 'roles'
    # 定义列对象
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(32),unique=True)
    users = db.relationship('User',backref='role')

    # repr()方法显示一个可读字符串
    def __repr__(self):
        return '<Role: %s %s>'%(self.name,self.id)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(32),unique=True,index=True)
    email = db.Column(db.String(32),unique=True)
    password = db.Column(db.String(32))
    # 外键: 表名.id
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User: %s %s %s %s>' % (self.name, self.id, self.email, self.password)


# @app.route('/', methods=['GET', 'POST'])
# def sql_demo():
#     return 'Hello World!'


if __name__ == '__main__':
    # 删除表
    db.drop_all()

    # 创建表
    db.create_all()

    app.run(debug=True)
