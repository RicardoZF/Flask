# -*- coding:utf-8 -*-
from flask import render_template
# 2, 在子模块中导入蓝图对象,实现路由的定义
from . import app_cart
# 2 使用蓝图对象实现路由定义
@app_cart.route('/cart_info')
def cart_info():
    return render_template('cart_info.html')

@app_cart.route('/cart_list')
def cart_list():
    return 'cart_list'
