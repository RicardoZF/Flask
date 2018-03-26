# -*- coding:utf-8 -*-

from flask import Flask, request, jsonify

app = Flask(__name__)


# 当参数不全的话，返回errcode=-2
# 当登录名和密码错误的时候，返回 errcode = -1
# 当登录成功之后，返回 errcode = 0
@app.route('/login', methods=['POST'])
def index():

    username = request.form.get('username')
    password = request.form.get('password')

    # 判断参数是否为空
    if not all([username, password]):
        result = {
            "errcode": -2,
            "errmsg": "params error"
        }
        return jsonify(result)
    # a = 1 / 0
    # 如果账号密码正确
    # 判断账号密码是否正确
    if username == 'itheima' and password == 'python':
        result = {
            "errcode": 0,
            "errmsg": "success"
        }
        return jsonify(result)
    else:
        result = {
            "errcode": -1,
            "errmsg": "wrong username or password"
        }
        return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)