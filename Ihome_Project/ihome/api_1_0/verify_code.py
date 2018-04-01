# -*- coding:utf-8 -*-
import logging

from ihome.libs.yuntongxun.sms import CCP
from ihome.models import User
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from flask import jsonify, make_response, request
from ihome.utils.response_code import RET
import random

# 获取图形验证码
# 请求方式:GET
@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    # 使用工具类生成验证码
    name, text, image_data = captcha.generate_captcha()

    # 将key:用户编号和value:验证码的数据存入redis
    try:
        # redis_store.set()
        # redis_store.expires()
        # setex:设置数据同时设置有效期.
        # 第一位:KEY ,第二位:有效期  第三位:VALUE
        redis_store.setex('image_code_%s' % image_code_id, 300, text)
    except Exception as e:
        # 记录日志
        logging.error(e)
        resp = {
            'errno': RET.DBERR,
            'errmsg': 'redis保存出错'
        }
        return jsonify(resp)
    a = redis_store.keys()
    print a
    # 返回图像
    resp = make_response(image_data)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


# 获取短信验证码
# 请求方式:GET
# 路由sms_codes
# 参数 手机号 图形验证码 编号
# URL:/api/v1_0/sms_codes/13612345678?image_code=w8rz&image_code_id=61242
@api.route('/sms_codes/<re("1[3456789][0-9]{9}"):mobile>')
def get_sms_codes(mobile):
    # 一 获取 图形验证码 编号
    image_code = request.args.get('image_code')
    image_code_id = request.args.get('image_code_id')

    # 二 校验参数是否完整
    if not all([image_code, image_code_id]):
        resp = {
            'erron': RET.PARAMERR,
            'errmsg': '参数不全'
        }
        return jsonify(resp)

    # 三 逻辑处理
    # 1 从redis中取数据
    # 1.1 获取数据,图形验证码
    try:
        real_image_code = redis_store.get('image_code_%s'%image_code_id)
    except Exception as e:
        logging.error(e)
        resp = {
            'erron': RET.DBERR,
            'errmsg': 'redis读取失败'
        }
        return jsonify(resp)

    # 1.2 判断是否为None
    # 数据库获取操作, 一定要判断None. 只要查询不出数据,就是返回None
    if real_image_code is None:
        resp = {
            'erron': RET.DBERR,
            'errmsg': '验证码已过期,请重新获取'
        }
        return jsonify(resp)
    # 1.3 删除redis中图形验证码 --> 验证码只能验证一次
    # 已获取了变量real_image_code,不影响1.4对比
    try:
        redis_store.delete('image_code_%s'%image_code_id)
    except Exception as e:
        logging.error(e)
        resp = {
            'erron': RET.DBERR,
            'errmsg': 'redis数据删除失败'
        }
        return jsonify(resp)

    # 1.4 对比图形验证码验证码时候否正确
    if image_code.lower() != real_image_code.lower():
        resp = {
            'erron': RET.DATAERR,
            'errmsg': '验证码填写错误,,请刷新后重试'
        }
        return jsonify(resp)

    # 2 判断手机号是否已注册
    # 2.1 从mysql中取用户数据
    try:
        user = User.query.filter_by(mobile = mobile).first()
    except Exception as e:
        logging.error(e)
        resp = {
            'erron': RET.DBERR,
            'errmsg': 'mysql查询失败'
        }
        return jsonify(resp)
    # 2.2 用户是否存在,存在,则已注册过了
    # print 'user' % user
    if user:
        resp = {
            'erron': RET.DATAEXIST,
            'errmsg': '用户已注册'
        }
        return jsonify(resp)

    # 3 发送短信验证码
    # 3.1 生成随机6位数
    # %06d: 6位数字, 不足以0补齐
    sms_code = '%06d'%random.randint(0,999999)
    ccp = CCP()
    result = ccp.send_template_sms(mobile, [sms_code, '5'], 1)

    # 3.2 try:将短信验证码保存redis中
    try:
        # 保存到redis中 setex: 可以设置数据并设置有效期
        # 需要三个参数: key , expiretime, value
        redis_store.setex('sms_code_' + mobile, 300, sms_code)
    except Exception as e:
        logging.error(e)
        resp_dict = {
            'errno': RET.DBERR,
            'errmsg': '保存验证码异常'
        }
        return jsonify(resp_dict)

    # 四 返回数据
    if result == '000000':
        resp = {
            'erron': RET.OK,
            'errmsg': '发送短信成功'
        }
    else:
        resp = {
            'erron': RET.THIRDERR,
            'errmsg': '发送短信失败'
        }
    return jsonify(resp)

