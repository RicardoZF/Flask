# -*- coding:utf-8 -*-
from flask import Blueprint,current_app
# 此文件,专门处理静态文件的访问,不做模板渲染,只转发文件路径
from flask import make_response
from flask_wtf.csrf import generate_csrf
"""
127.0.0.1:5000  index.html
127.0.0.1:5000/login.html login.html
/favicon.ico 固定访问的名字,我们需要处理浏览器发出的访问网站小图标的请求
"""
# 定义蓝图对象
html = Blueprint('html',__name__)

# 实现路由
@html.route('/<re(".*"):file_name>')
def wed_html(file_name):
    """提供html静态文件"""
    if not file_name:
        # 表示用户访问的是 '/'
        file_name = 'index.html'

    # 判断如果不是网站logo
    if file_name != 'favicon.ico':
        # 拼接路径
        file_name = 'html/' + file_name

    # print file_name
    # favicon.ico  会再第一次访问网址时发送请求,然后缓存起来
    # 发送静态资源,而不是渲染模板,
    # send_static_file 默认指向static下

    # 创建response
    response = make_response(current_app.send_static_file(file_name))
    # 设置csrf_token
    csrf_token = generate_csrf()

    # 设置cookie
    response.set_cookie('csrf_token',csrf_token)
    # Flask-WTF的generate_csrf, 会将cookie中的csrf_token信息, 会同步到session中
    # Flask-Session又会讲session中的csrf_token, 同步到redis中
    # generate_csrf不会每次调用都生成. 会先判断浏览器的cookie中的session里是否有csrf_token信息.没有才重新生成
    # 常规的CSRF保护机制, 是从浏览器的cookie中获取. 而Flask-WTF的扩展机制不一样, 是从session信息中获取csrf_token保护机制

    return response