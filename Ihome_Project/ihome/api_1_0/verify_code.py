# -*- coding:utf-8 -*-
import logging
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from flask import jsonify,make_response
from ihome.utils.response_code import RET
# 获取图形验证码
# 请求方式:GET
@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    # 使用工具类生成验证码
    name,text,image_data = captcha.generate_captcha()

    # 将key:用户编号和value:验证码的数据存入redis
    try:
        # redis_store.set()
        # redis_store.expires()
        # setex:设置数据同时设置有效期.
        # 第一位:KEY ,第二位:有效期  第三位:VALUE
        redis_store.setex('image_code_%s'%image_code_id,300,text)
    except Exception as e:
        # 记录日志
        logging.error(e)
        resp = {
            'errno':RET.DBERR,
            'errmsg':'redis保存出错'
        }
        return jsonify(resp)
    a = redis_store.keys()
    print a
    # 返回图像
    resp = make_response(image_data)
    resp.headers['Content-Type']='image/jpg'
    return resp