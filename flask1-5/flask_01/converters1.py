# -*- coding:utf-8 -*-

# 导包 BaseConverter --> 所有路由转换器的基类
from werkzeug.routing import BaseConverter

# 模仿系统的方式,自定义一个转换器
class RegexConverter(BaseConverter):
    # 为增加参数,重写init  map 就是 url_map
    def __init__(self,url_map,*args):
        # 覆盖父类regex
        super(RegexConverter,self).__init__(url_map)
        self.regex = args[0]

# 添加到系统

# 使用