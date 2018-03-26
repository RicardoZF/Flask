# -*- coding:utf-8 -*-
from flask import Flask, jsonify
from flask import json
from flask import redirect
from flask import url_for

app = Flask(__name__)

# HEAD:只会返回头数据,可计算文件大小
# OPTIONS:比HEAD多一个请求方式信息
@app.route('/',methods=['GET','POST'])
def hello_world():
    return 'Hello World!'

@app.route('/num/<num_id>')
def num_dome(num_id):
    #  num_id 默认是字符串
    return 'num_id:%s'%num_id

@app.route('/redirect')
def redirect_demo():
    # 方式一: 使用redirect
    # return redirect('http://www.itcast.cn')

    # 方式二 使用redirect和url_for,可传参
    return redirect(url_for('num_dome',num_id=666))

# 返回JSON数据
@app.route('/json')
def json_demo():
    dict = {
        'name':'小白',
        'age':1
    }
    # 方式一: 使用json.dumps()
    # - 仅仅是将字典转换为JSON格式的字符串.
    # - 返回的响应头Content - Type为text / html

    # return json.dumps(dict)

    # 如果要实现和方式二一样的效果, 可以使用如下方式
    # return 第一个参数: 返回的数据, 第二个参数: 状态码, 第三个参数: 设置响应头信息
    # return json.dumps(dict), 200, {'Content-Type': 'application/json'}

    # 方式二: 使用jsonify()
    #  除了将字典转换为JSON格式的字符串
    # - 同时会设置响应头Content-Type为application/json
    # - 建议使用jsonify, 前后端分离的项目中, 前后端都通过JSON进行数据交流
    return jsonify(dict)


if __name__ == '__main__':
    # 查看路由信息,记录路由与视图函数的映射关系和请求方式
    print app.url_map
    app.run(debug=True)