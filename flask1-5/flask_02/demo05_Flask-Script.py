# -*- coding:utf-8 -*-

from flask import Flask
from flask_script  import Manager

app = Flask(__name__)

# 把 Manager 类和应用程序实例进行关联,托管程序
manager = Manager(app)

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    # app.run()
    # 使用manager运行
    manager.run()
