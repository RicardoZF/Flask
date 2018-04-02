# -*- coding:utf-8 -*-
import logging
from . import api
from ihome.utils.common import login_required
from flask import request,g,jsonify,session
from ihome.utils.response_code import RET
from ihome.libs.image_storage import storage
from ihome.models import User
from ihome import db
from ihome.utils import constants

# 参数 用户id 图片
@api.route('/users/avatar',methods=['POST'])
@login_required
def set_user_avatar():
    """设置用户头像"""
    # 一 获取参数
    # 图片是以表单提交的
    # 用户id
    user_id = g.user_id
    # 图片对象
    img_file = request.files.get('avatar')

    # 二 校验参数
    if img_file is None:
        return jsonify(errno=RET.PARAMERR,errmsg='未上传图片')

    # 三 逻辑处理
    # 保存图像
    # 1.读取图像二进制数据
    img_data = img_file.read()
    # 2.上传到七牛云
    try:
        # file_name 就存储的是图片名. 将来就可以再程序中调用显示
        file_name = storage(img_data)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='上传图像异常')
    # 3.保存到mysql
    try:
        # update: 查询之后拼接update, 可以直接进行更新操作
        # update中需要传入字典
        User.query.filter_by(id=user_id).update({'avatar_url':file_name})
        # update需要commit
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='mysql更新头像数据异常')
    # 四 返回数据
        # 此时的文件名, 没有域名. 因此如果直接返回给客户端, 客户端无法直接加载
        # ozcxm6oo6.bkt.clouddn.com
        # 为了避免在数据库存储过多重复的域名前缀, 因此保存的时候, 不加域名
        # 返回给前端数据时, 我们拼接域名即可

    # 拼接完整路径
    avatar_url = constants.QINIU_URL_DOMAIN+file_name

    # 返回的时候, 记得添加图像url信息
    # 如果还需要额外的返回数据, 可以再后方自行拼接数据, 一般会封装成一个字典返回额外数据
    return jsonify(errno=RET.OK, errmsg='上传成功',data={'avatar_url':avatar_url})

# 参数 用户id  要设置的用户名
@api.route('/users/name',methods=['PUT'])
@login_required
def change_user_name():
    """修改用户名"""
    # 获取用户id
    user_id = g.user_id
    # 获取设置的用户名
    req_data = request.get_json()
    name = req_data.get('name')
    # 校验参数
    if name is None:
        return jsonify(errno=RET.NODATA,errmsg='用户名不能为空')

    # 保存数据到mysql
    try:
        User.query.filter_by(id=user_id).update({'name':name})
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='mysql保存name异常')

    # 修改session数据中的name字段
    session['user_name']=name
    return jsonify(errno=RET.OK, errmsg='OK',data={'name':name})


@api.route('/users', methods=["GET"])
@login_required
def get_user_info():
    """个人信息获取"""
    user_id = g.user_id
    # 从数据库获取信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取用户信息失败')

    if user is None:
        return jsonify(errno=RET.NODATA,errmsg='无效操作')

    return jsonify(errno=RET.OK, errmsg='OK',data=user.to_dict())


# @api.route('/users/auth', methods=['POST'])
# @login_required
# def set_user_auth():
#     """设置实名认证信息"""
#     user_id = g.user_id
#     # 获取参数
#     req_data = request.get_json()
#     if not req_data:
#         return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
#
#     # 真实姓名,身份证号
#     real_name = req_data.get('real_name')
#     id_card = req_data.get('id_card')
#     # 校验参数
#     if not all([real_name,id_card]):
#         return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
#
#     # 保存到数据库
#         # 保存用户的姓名与身份证号
#     try:
#         User.query.filter_by(id=user_id, real_name=None, id_card=None) \
#             .update({"real_name": real_name, "id_card": id_card})
#         db.session.commit()
#     except Exception as e:
#         logging.error(e)
#         db.session.rollback()
#         return jsonify(errno=RET.DBERR, errmsg="保存用户实名信息失败")
#
#     return jsonify(errno=RET.OK, errmsg="OK")

@api.route("/users/auth", methods=["POST"])
@login_required
def set_user_auth():
    """保存实名认证信息"""
    user_id = g.user_id

    # 获取参数
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    real_name = req_data.get("real_name")  # 真实姓名
    id_card = req_data.get("id_card")  # 身份证号

    # 参数校验
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 保存用户的姓名与身份证号
    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None)\
            .update({"real_name": real_name, "id_card": id_card})
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户实名信息失败")

    return jsonify(errno=RET.OK, errmsg="OK")


@api.route('/users/auth', methods=['GET'])
@login_required
def get_user_auth():
    """获取用户认证信息"""
    user_id = g.user_id

    # 从mysql中获取数据
    try:
        user = User.query.get(user_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库查询异常')

    if user is None:
        return jsonify(errno=RET.NODATA,errmsg='无效操作')

    return jsonify(errno=RET.OK, errmsg='OK',data=user.auth_to_dict())