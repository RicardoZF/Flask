# -*- coding:utf-8 -*-
'''
如果是目录形式实现蓝图
1, 在模块的__init__文件中,导入蓝图,创建蓝图对象,以及导入子模块
2, 在子模块中导入蓝图对象,实现路由的定义
3,在app创建的地方注册蓝图
'''

from flask import Blueprint
# 1,创建蓝图对象
# 蓝图对象名           蓝图名称
app_cart = Blueprint('cart',__name__,template_folder='cart_templates')

# 导入使用蓝图的子模块
import view1,view2