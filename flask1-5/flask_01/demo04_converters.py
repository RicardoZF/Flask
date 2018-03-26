# -*- coding:utf-8 -*-
from flask import Flask

from converters import RegexConverter

app = Flask(__name__)


# 添加到系统
app.url_map.converters['re']=RegexConverter
# 使用

# 自定义正则表达式,过滤路由

@app.route('/login/<re(r"1[3456789][0-9]{9}"):mobile>')
def hello_world(mobile):
    # return 'Hello World!'
    return 'mobile: %s'%mobile

if __name__ == '__main__':
    app.run(debug=True)