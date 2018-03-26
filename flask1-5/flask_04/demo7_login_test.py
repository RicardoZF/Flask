# -*- coding:utf-8 -*-

# 导入单元测试
import unittest
import json
from demo6_login import app


# 自定义测试类 --> 针对一种测试定义一个类, 类中会定义多个函数, 来测试多个测试用例

# 如果要全部测试, 在顶部或底部空白处运行即可. 如果要单独测试, 光标定位在该方法执行即可
class LoginTestCase(unittest.TestCase):

    # 该方法会首先执行，相当于做测试前的准备工作
    def setUp(self):
        # 开启测试模式, 方便调试用的
        app.testing = True
        self.client = app.test_client()


    #TODO(zhubo) 还有其他3个测试用例, 自己补充

    # 输入了正确的用户名和密码的情况
    def test_right_username_password(self):
        response = self.client.post('/login', data={'username':'itheima', 'password':'python'})
        response_data = response.data
        response_dict = json.loads(response_data)
        self.assertIn('errcode', response_dict, 'must have errcode')
        self.assertEqual(0, response_dict['errcode'], 'errcode must is 0')


    # 测试用例, 必须以test_开头, 否则系统无法识别
    # 没有输入用户名和密码的情况
    def test_empty_username_password(self):

        # 核心逻辑: 用测试客户端, 发出post请求, 获取参数, 进行断言

        # 1. 获取测试客户端
        # client = app.test_client()

        # 2. 发出post请求 (第一个参数:路由地址  第二个参数: 发送的数据, 以字典方式传入)
        response = self.client.post('/login', data={})

        # 3. 获取参数
        response_data = response.data

        # 4. 将字符串转换为字典
        # json.dumps() 将字典转为字符串
        response_dict = json.loads(response_data)

        # 5. 进行断言--> 先判断是否有errcode
        self.assertIn('errcode', response_dict, 'must have errcode')

        # 6. 进行断言--> 再判断errcode是否相等于-2
        self.assertEqual(-2, response_dict['errcode'], 'errcode must is -2')

