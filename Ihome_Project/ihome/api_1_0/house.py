# -*- coding:utf-8 -*-

import logging
from . import api
from ihome import redis_store
from ihome.models import Area
from flask import jsonify,json
from ihome.utils.response_code import RET
from ihome.utils import constants
# 获取城区信息
@api.route('/areas')
def get_areas_info():
    """
    1.读取redis缓存
    2.没缓存,去mysql查
    3.存入redis
    4.返回json数据
    """
    # 1.读取redis缓存
    try:
        area_json = redis_store.get('area_info')
    except Exception as e:
        logging.error(e)
        area_json = None

    # 2.没缓存,去mysql查
    if area_json is None:
        try:
            area_list = Area.query.all()
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库查询异常')

        # 3. 利用模型类中方法,将areas对象列表转化为一个个字典,再利用列表推导式将这些字典变为列表
        # 最后就将数据转为json格式,方便redis读取
        areas_dict = {'areas':[area.to_dict() for area in area_list]}
        # 1L-->ASCII编码 --> 改变编码格式
        area_json = json.dumps(areas_dict)
        # print 'area_jsons%s'%area_json
        # 4.存入redis  key 过期时间 value
        try:
            redis_store.setex('area_info',constants.AREA_INFO_REDIS_EXPIRES,area_json)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR, errmsg='redis存储异常')
    # area_json = json.loads(area_json)
    # return jsonify(errno=RET.OK, errmsg='城区信息获取成功',data=area_json)
    # 前面已经将区域数据转为JSON了. 这里不需要再次调用jsonify来返回, 直接返回字典格式的信息即可
    return '{"errno":0, "errmsg":"查询城区信息成功","data":%s}' % area_json




