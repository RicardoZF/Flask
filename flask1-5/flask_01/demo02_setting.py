# -*- coding:utf-8 -*-
from flask import Flask

from settings import Config

app = Flask(__name__,
            static_folder='static')

"""
调试模式
1,自动重启服务器(鼠标离开或保存py文件)
2,控制台会打印error
"""
# 方式1,属性
# app.debug = True

# 方式2
# config,是一个存储app所有配置的字典,Key都是大写
# app.config['DEBUG']= True

# 方式3 加载文件,完整文件名
# app.config.from_pyfile('settings.py')

# 方式4 , 加载对象(更为推荐)
app.config.from_object(Config)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    # app的一些参数
    # 默认  port:5000  host:'127.0.0.1'
    # app.run(debug=True,port=5001,host='192.168.44.129 ')

    # 全零地址:本机/局域网/公网都可访问
    app.run(debug=True,host='0.0.0.0')