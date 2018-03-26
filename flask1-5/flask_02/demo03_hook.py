# -*- coding:utf-8 -*-
from flask import Flask

app = Flask(__name__)


@app.route('/')
def func():
    print '666666666'
    return '666'


# before_first_request：在处理第一个请求前运行。
# before_request：在每次请求前运行。
# after_request：没有异常抛出，在每次请求后运行,需要接受响应数据。
# teardown_request：在每次请求后运行，即使有未处理的异常抛出,需要接收服务器异常信息

# 在处理第一个请求前运行. 应用场景: 比如连接数据库操作
@app.before_first_request
def before_first_request():
    print '在处理第一个请求前运行'


# 在每次请求前运行。应用场景: 比如对数据做效验. 如果数据有问题, 可以直接返回. 就不会再去执行对应的视图函数
@app.before_request
def before_request():
    print '在每次请求前运行'


# 如果没有未处理的异常抛出, 在每次请求后运行。应用场景: 比如拼接响应头信息. 让所有json.dumps()的数据, 统一增加Content-Type为application/json
@app.after_request
def after_request(response):
    response.headers['Content-Type'] = 'application/json'
    print '如果没有未处理的异常抛出，在每次请求后运行。response:%s' % response
    return response


# 在每次请求最后运行，即使有未处理的异常抛出。 可以捕获到异常信息,存入日志
@app.teardown_request
def teardown_request(error):
    print '在每次请求后运行，即使有未处理的异常抛出error:%s' % error


if __name__ == '__main__':
    app.run(debug=True)
