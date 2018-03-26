# -*- coding:utf-8 -*-
from flask import Flask,abort

app = Flask(__name__)


@app.route('/abort')
def abort_demo():
    # 制造异常
    abort(404)
    # a = 1/0  # 会产生 ZeroDivisionError 异常
    return 'Hello World!'

@app.errorhandler(404)
def server_error(error):
    # error 不需要给用户显示,可存在错误日志
    # 写状态码,为了保持一致
    print 'error:%s'%error
    return '网页找不到了',404

# 捕获其他异常
# @app.errorhandler(ZeroDivisionError)
# def server_error(error):
#     return '0不能做除数,404


if __name__ == '__main__':
    app.run(debug=True)