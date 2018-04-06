# -*- coding:utf-8 -*-

import logging
from . import api
from ihome import redis_store, db
from ihome.models import Area, User, House, Facility, HouseImage, Order
from flask import jsonify, json, request, session
from ihome.utils.response_code import RET
from ihome.utils import constants
from ihome.utils.common import login_required, g
from ihome.libs.image_storage import storage
from datetime import datetime


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
        areas_dict = {'areas': [area.to_dict() for area in area_list]}
        # 1L-->ASCII编码 --> 改变编码格式
        area_json = json.dumps(areas_dict)
        # print 'area_jsons%s'%area_json
        # 4.存入redis  key 过期时间 value
        try:
            redis_store.setex('area_info', constants.AREA_INFO_REDIS_EXPIRES, area_json)
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
    if not all(
            [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 2.对数字进行判断(价格/关联外键id)
    try:
        # 将价格转化成以分为单位
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
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

    # 使用工具类上传房屋图片
    image_data = image_file.read()
    try:
        file_name = storage(image_data)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="图片上传失败")

    # 保存到数据库
    # 1.保存到HouseImage
    house_img = HouseImage(
        url=file_name,
        house_id=house_id
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
    return jsonify(errno=RET.OK, errmsg='房屋图片设置成功', data={'image_url': image_url})


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
            redis_store.setex("home_page_data", constants.HOME_PAGE_DATA_REDIS_EXPIRES, json_houses)
        except Exception as e:
            logging.error(e)
        # 返回数据
        return '{"errno":0, "errmsg":"OK", "data":%s}' % json_houses


@api.route("/houses/<int:house_id>", methods=["GET"])
def get_house_detail(house_id):
    """获取房屋详情"""
    # 前端在房屋详情页面展示时，如果浏览页面的用户不是该房屋的房东，则展示预定按钮，否则不展示，
    # 所以需要后端返回登录用户的user_id
    # 尝试获取用户登录的信息，若登录，则返回给前端登录用户的user_id，否则返回user_id=-1
    user_id = session.get("user_id", "-1")

    # 校验参数
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")

    # 先从redis缓存中获取信息
    try:
        ret = redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        logging.error(e)
        ret = None
    if ret:
        # logging.info("hit house info redis")
        return '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, ret), 200, {
            "Content-Type": "application/json"}

    # 查询数据库
    try:
        house = House.query.get(house_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 将房屋对象数据转换为字典
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据出错")

    # 存入到redis中
    json_house = json.dumps(house_data)
    try:
        redis_store.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, json_house)
    except Exception as e:
        logging.error(e)

    resp = '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, json_house)
    return resp


# /api/v1_0/houses?sd=xxxx-xx-xx&ed=xxxx-xx-xx&aid=xx&sk=new&p=1
@api.route("/houses", methods=["GET"])
def get_house_list():
    """获取房屋列表信息"""
    # 一. 获取参数
    # 注意: 参数可以不传, 不传就把参数设为空值或者默认值
    start_date_str = request.args.get("sd", "")  # 想要查询的起始时间
    end_date_str = request.args.get("ed", "")  # 想要查询的终止时间
    area_id = request.args.get("aid", "")  # 区域id
    sort_key = request.args.get("sk", "new")  # 排序关键字
    page = request.args.get("p", 1)  # 页数

    # 二. 校验参数
    # 2.1 判断日期,确保能转成日期格式,开始日期不能大于结束日期
    try:
        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

        if start_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        if start_date and end_date:
            assert start_date <= end_date

    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期参数有误")

    # 2.2 判断页数,能转为int
    try:
        page = int(page)
    except Exception:
        page = 1

    # 三. 逻辑处理
    # 3.1 从redis中取数据,有数据,直接返回
    try:
        redis_key = 'houses_%s_%s_%s_%s'%(start_date_str,end_date_str, area_id, sort_key)
        resp_json = redis_store.hget(redis_key,page)
    except Exception as e:
        logging.error(e)
        resp_json = None

    if resp_json:
        return resp_json

    # 3.2 从mysql中取数据
    # 3.2.1 定义空列表,方便存放查询条件
    filter_params = []

    # 3.2.2 区域信息
    if area_id:
        filter_params.append(House.area_id == area_id)

    # 3.2.3 处理时间, 获取不冲突的房屋信息
    # 先获取冲突的订单信息,自定义起始日期<=订单结束日期 and  自定义结束 >= 订单开始
    orders_conflict_li = []
    try:
        if start_date and end_date:
            orders_conflict_li = Order.query.filter(start_date <= Order.end_date, end_date >= Order.begin_date).all()
        elif start_date:
            orders_conflict_li = Order.query.filter(start_date <= Order.end_date).all()
        elif end_date:
            orders_conflict_li = Order.query.filter(end_date >= Order.begin_date).all()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="mysql查询异常")

    if orders_conflict_li:
        house_id_conflict_li = [order.house_id for order in orders_conflict_li]
        # 添加不冲突的房屋条件到列表
        filter_params.append(House.id.notin_(house_id_conflict_li))

    # 3.2.4 排序
    # 订单量  "booking"  desc
    # 价格  "price-inc"  asc ; "price-des" desc
    # 上架时间 desc
    if sort_key == "booking":
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == "price-inc":
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == "price-des":
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    # 3.2.5 分页
    try:
        #                              页数    房屋列表页面每页的数量              错误输出
        house_page = house_query.paginate(page,constants.HOUSE_LIST_PAGE_CAPACITY,False)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    house_li = house_page.items  # 当前页的数据
    total_page = house_page.pages  # 总页数

    houses = []
    for house in house_li:
        houses.append(house.to_basic_dict())

    # 将结果转为json字符串
    resp = dict(errno=RET.OK, errmsg="查询成功",
                data={"houses": houses, "total_page": total_page, "current_page": page})
    resp_json = json.dumps(resp)
    # 3.3 存入redis
    if page <= total_page:
        # 用redis的哈希类型保存分页数据
        redis_key = "houses_%s_%s_%s_%s" % (start_date_str, end_date_str, area_id, sort_key)

        try:
            # 使用redis中事务
            pipeline = redis_store.pipeline()
            # 开启事务
            pipeline.multi()
            pipeline.hset(redis_key,page,resp_json)
            pipeline.expire(redis_key,constants.HOUSE_LIST_PAGE_REDIS_EXPIRES)
            # 执行事务
            pipeline.execute()
        except Exception as e:
            logging.error(e)

    # 四. 返回数据
    return resp_json