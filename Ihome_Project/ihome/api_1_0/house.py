# -*- coding:utf-8 -*-

import logging
from . import api
from ihome import redis_store, db
from ihome.models import Area,User,House,Facility,HouseImage
from flask import jsonify,json,request
from ihome.utils.response_code import RET
from ihome.utils import constants
from ihome.utils.common import login_required,g
from ihome.libs.image_storage import storage

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

# 设置房屋信息
@api.route("/houses/info", methods=["POST"])
@login_required
def save_house_info():
    """保存房屋的基本信息
       前端发送过来的json数据
       {
           "title":"",
           "price":"",
           "address":"",
           "room_count":"",
           "acreage":"",
           "unit":"",
           "capacity":"",
           "beds":"",
           "deposit":"",
           "min_days":"",
           "max_days":"",
           "area_id":"1",
           "facility":["7","8"]
       }
       """
    # 一 获取参数
    house_data = request.get_json()
    if house_data is None:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    title = house_data.get("title")  # 房屋名称标题
    price = house_data.get("price")  # 房屋单价
    area_id = house_data.get("area_id")  # 房屋所属城区的编号
    address = house_data.get("address")  # 房屋地址
    room_count = house_data.get("room_count")  # 房屋包含的房间数目
    acreage = house_data.get("acreage")  # 房屋面积
    unit = house_data.get("unit")  # 房屋布局（几室几厅)
    capacity = house_data.get("capacity")  # 房屋容纳人数
    beds = house_data.get("beds")  # 房屋卧床数目
    deposit = house_data.get("deposit")  # 押金
    min_days = house_data.get("min_days")  # 最小入住天数
    max_days = house_data.get("max_days")  # 最大入住天数

    # 二 校验参数
    # 1.完整性
    if not all([title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")


    # 2.对数字进行判断(价格/关联外键id)
    try:
        # 将价格转化成以分为单位
        price = int(float(price)*100)
        deposit = int(float(deposit)*100)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 三 逻辑处理
    # 1.创建House模型
    user_id = g.user_id
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # 2.判断是够有房屋配置信息facility,有则添加
    facility_id_list = house_data.get("facility")
    if facility_id_list:
        try:
            facility_list = Facility.query.filter(Facility.id.in_(facility_id_list)).all()
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR, errmsg="mysql查询异常")

        if facility_list:
            house.facilities = facility_list
    # 3.添加数据库
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="mysql保存异常")

    # 四 返回数据
        # 四. 返回
    return jsonify(errno=RET.OK, errmsg="保存成功", data={"house_id": house.id})

# 发布房屋图片接口
# 房屋id / 图片
# 逻辑: 1. 上传到七牛云 2. 保存数据库:需要2个地方 house/houser_image
@api.route("/houses/image", methods=["POST"])
@login_required
def save_house_image():
    """保存房屋的图片"""
    # 获取参数 房屋的图片、房屋编号
    house_id = request.form.get("house_id")
    image_file = request.files.get("house_image")

    # 校验参数
    if not all([house_id, image_file]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断house是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="mysql查询异常")

    if house is None:
        return jsonify(errno=RET.NODATA, errmsg="无此房屋")

    #  使用工具类上传房屋图片
    image_data = image_file.read()
    try:
        file_name = storage(image_data)
    except Exception as e:
        logging.error(e)
        return jsonify(errno= RET.THIRDERR, errmsg="图片上传失败")

    # 保存到数据库
    # 1.保存到HouseImage
    house_img= HouseImage(
        url = file_name,
        house_id = house_id
    )
    db.session.add(house_img)
    # 2.增加房屋模型的字段数据
    if not house.index_image_url:
        # 没有主图信息,才添加
        house.index_image_url = file_name
        db.session.add(house)

    # 3.统一提交
    try:
        db.session.commit()

    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="房屋图片保存失败")

    # 返回数据
    image_url = constants.QINIU_URL_DOMAIN + file_name
    return jsonify(errno=RET.OK, errmsg='房屋图片设置成功',data={'image_url':image_url})

@api.route("/users/houses", methods=["GET"])
@login_required
def get_user_houses():
    """获取房东发布的房源信息条目"""
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库查询异常")

    houses_list = []
    if houses:
        for house in houses:
            houses_list.append(house.to_basic_dict())

    return jsonify(errno=RET.OK, errmsg="OK", data={"houses": houses_list})


@api.route("/houses/index", methods=["GET"])
def get_house_index():
    """获取主页幻灯片展示的房屋基本信息"""
    # 尝试从redis里取
    try:
        ret = redis_store.get("home_page_data")
    except Exception as e:
        logging.error(e)
        ret = None
    # redis有数据,直接返回
    if ret:
        logging.info("hit house index info redis")
        # 因为redis中保存的是json字符串，所以直接进行字符串拼接返回
        return '{"errno":0, "errmsg":"OK", "data":%s}' % ret
    # redis没数据,从mysql中取
    else:
        try:
            # 查询数据库，返回房屋订单数目最多的5条数据
            houses = House.query.order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
        if not houses:
            return jsonify(errno=RET.NODATA, errmsg="查询无数据")

        houses_list = []
        for house in houses:
            if not house.index_image_url:
                continue
            houses_list.append(house.to_basic_dict())

        # 将数据存入redis
        json_houses = json.dumps(houses_list)
        try:
            redis_store.setex("home_page_data",constants.HOME_PAGE_DATA_REDIS_EXPIRES,json_houses)
        except Exception as e:
            logging.error(e)
        # 返回数据
        return '{"errno":0, "errmsg":"OK", "data":%s}' % json_houses
