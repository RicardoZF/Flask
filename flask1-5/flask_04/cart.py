# -*- coding:utf-8 -*-
from flask import Blueprint,render_template
# 1,创建蓝图对象
# 蓝图对象名           蓝图名称
app_cart = Blueprint('cart',__name__)


# 2 使用蓝图对象实现路由定义
@app_cart.route('/cart_info')
def cart_info():
    return render_template('index.html')

@app_cart.route('/cart_list')
def cart_list():
    return 'cart_list'