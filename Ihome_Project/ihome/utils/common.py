# -*- coding:utf-8 -*-
from flask import g,session,jsonify
from response_code import RET
from functools import wraps
def login_required(view_func):
    """检查用户登陆状态"""
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        # 核心逻辑,获取用户id
        user_id = session.get('user_id')
        if user_id:
            # 表示用户已登陆
            # 后面接口调用该验证,仍可能用到user_id,所以用g变量记录
            g.user_id = user_id
            return view_func(*args,**kwargs)
        else:
            return jsonify(errno=RET.SESSIONERR,errmsg='用户未登陆')
    return wrapper
