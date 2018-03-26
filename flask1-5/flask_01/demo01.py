# -*- coding:utf-8 -*-
from flask import Flask,render_template


# import_name: 模块名
app = Flask(__name__,
            static_url_path = '/img',  # 设置访问路径,默认是static
            static_folder='static')  # 设置查找路径

# 装饰器的作用是将路由映射到视图函数index
@app.route('/')
def hello_world():
    return 'Hello World!'
    # return render_template('index.html')

if __name__ == '__main__':
    # Flask应用程序实例的run方法启动WEB服务器
    app.run(debug=True)