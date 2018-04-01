# -*- coding:utf-8 -*-
import logging

from ihome.models import User
from ihome.utils.response_code import RET
from . import api
from flask import request, jsonify,current_app,session
import re
from ihome import redis_store, db


# 参数:手机号,短信验证码,密码
# URL:/api/v1_0/users?mobile=13612345678&sms_code=1234&password=123456
@api.route('/users', methods=['POST'])
def register():
    """注册"""
    # 一 获取参数(前后端分离,用json格式数据传输)
    # data = request.data  # '{ "mobile":"136" }'  字符串格式（json格式）
    # get_data=request.get_data()  # '{ "mobile":"136" }'　字符串格式（json格式）
    # get_json=request.get_json()  # { u"mobile":u"136" }　字典格式
    get_json = request.get_json()
    mobile = get_json.get('mobile')
    sms_code = get_json.get('sms_code')
    password = get_json.get('password')

    # 二 校验参数
    # 1 完整性
    if not all([mobile,sms_code,password]):
        # resp = {
        #     'erron': RET.PARAMERR,
        #     'errmsg': '参数不全'
        # }
        # return jsonify(resp)
        # 这种写法,更为简单
        return jsonify(errno = RET.PARAMERR,errmsg='参数不全')

    # 2 手机号格式是否正确
    if not re.match(r"^1[3456789][0-9]{9}$",mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式有误')

    # 三 逻辑判断
    # 1 redis中获取数据对比
    # 1.1 try:从redis中获取短信验证码
    try:
        real_sms_code = redis_store.get('sms_code_%s'%mobile)
    except Exception as e:
        # 日志模块默认集成到了app中
        # current_app.logger.error(e)  (没有提示,没有logging.error(e)好用)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='redis读取错误')

    # 1.2 判断是否为None(是否过期)
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码已过期')

    # 1.3 对比短信验证码
    if sms_code != real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码填写错误')
    # 1.4 删除redis中短信验证码
    # try:删除短信验证码(如果验证出错重新发送的话, 浪费资源, 浪费用户时间) 跟之前的发送短信验证码3,4步是相反的
    try:
        redis_store.delete('sms_code_%s'%mobile)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg='redis删除失败')
    # 2 判断用户是否注册过,没注册就创建并保存用户(密码保存,会在模型中加密处理)
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR,errmsg='mysql查询错误')
    else:
        if user:
            # 用户已存在于数据库中
            return jsonify(errno=RET.DATAEXIST, errmsg='用户已注册')
    # 用户未注册 --> 创建用户对象并保存
    user = User(name = mobile,mobile =mobile)
    # 密码的加密处理, 应该交给模型类去处理.
    # user.password_hash = password
    # 利用模型类中setter方法执行加密处理
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        # 失败需回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='mysql添加失败')

    # 3 (注册后直接登陆)保存session
    try:
        session['user_id']=user.id
        session['user_name']=mobile
        session['user_mobile']=mobile
    except Exception as e:
        logging.error(e)
        return jsonify(errno = RET.SESSIONERR,errmsg='session设置失败')

    # 四 返回结果
    return jsonify(errno=RET.OK,errmsg='注册成功')

