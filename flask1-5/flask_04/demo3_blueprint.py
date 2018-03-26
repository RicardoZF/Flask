# -*- coding:utf-8 -*-

from flask import Flask
from order import order_info

app = Flask(__name__)

# 要实现模块化, 必须让app创建的文件, 知道其他路由的存在
'''
1. 导入子模块:
    cannot import name cart_info 无法导入: 发生了循环导入

2. 强制断掉循环. 有一方不能导入:
    没有app, 使用装饰器等价方式实现, 虽然可以, 但是不合适
    因为有一个路由, 就需要等价写一次
'''
app.route('/order_info')(order_info)

# 3, 导入蓝图对象,注册应用
from cart import app_cart
app.register_blueprint(app_cart,)


# @app.route('/order_info')
# def order_info():
#     return 'order_info'
#
# @app.route('/order_list')
# def order_list():
#     return 'order_list'
#
# @app.route('/cart_info')
# def cart_info():
#     return 'cart_info'
#
# @app.route('/cart_list')
# def cart_list():
#     return 'cart_list'



if __name__ == '__main__':
    print app.url_map
    app.run(debug=True)