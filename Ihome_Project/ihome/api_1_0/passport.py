# -*- coding:utf-8 -*-
import logging

from ihome.models import User
from ihome.utils.response_code import RET
from ihome.utils.common import login_required
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

# URL:/api/v1_0/sessions
# 参数: mobile password
@api.route('/sessions', methods=['POST'])
def login():
    """登陆"""
    # 一 获取参数
    get_json = request.get_json()
    mobile = get_json.get('mobile')
    password = get_json.get('password')
    # 二 校验参数
    # 1 参数完整性
    if not  all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errms='参数不全')
    # 2 手机号格式是否正确
    if not re.match(r"^1[3456789][0-9]{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式有误')

    # 三 逻辑处理
    # 1.从redis中获取登陆的次数-->超过最大次数5次,直接返回
    # 获取远程ip
    user_ip = request.remote_addr
    try:
        # 查询错误次数
        err_count = redis_store.get('user_error_count_%s'%user_ip)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg='redis读取错误次数失败')
    # 2.未超过5次,判断用户是否存在或密码是否正确,如果有问题则返回错误,并增加错误次数
    # 2.1 如果用户存在并且错误次数大于5,直接返回
    if err_count is not None and int(err_count) >=5 :
        return jsonify(errno=RET.REQERR, errmsg='错误次数已达上限,请明日后再登陆')
    # 获取用户
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg='mysql查询错误')

    # 用户名或密码错误,返回错误信息,增加错误次数
    if user is None or not user.check_password(password):
        try:
            # 累加错误次数,设置过期时间 一天
            # incr:累加错误次数
            redis_store.incr('user_error_count_%s'%user_ip)
            redis_store.expire('user_error_count_%s'%user_ip,86400)
        except Exception as e:
            logging.error(e)
        return jsonify(errno=RET.LOGINERR, errmsg='用户名或密码错误')

    # 3.设置session数据
    try:
        session['user_id']=user.id
        session['user_name']=user.name
        session['user_mobile']=user.mobile
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.SESSIONERR, errmsg='用户信息session设置失败')

    # 4.登陆成功,删除记录的错误次数
    try:
        redis_store.delete('user_error_count_%s'%user_ip)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg='redis错误次数删除失败')

    # 四 返回数据
    return jsonify(errno=RET.OK, errmsg='登陆成功')


@api.route('/sessions',methods=['GET'])
def check_login():
    '''检查登陆状态'''
    # 从session中获取用户name
    name = session.get('user_name')
    # 有name代表登陆,无,未登陆
    if name is None:
        return jsonify(errno=RET.SESSIONERR,errmsg='false')
    else:
        return jsonify(errno=RET.OK, errmsg='true',data={'name':name})


@api.route('/sessions',methods=['DELETE'])
@login_required
def logout():
    """登出"""
    # 清除session数据,csrf_token需要保留
    csrf_token = session['csrf_token']
    session.clear()
    session['csrf_token']=csrf_token

    return jsonify(errno=RET.OK,errmsg='OK')