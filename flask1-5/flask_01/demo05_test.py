# -*- coding:utf-8 -*-
from flask import Flask,render_template,redirect,json,jsonify
from flask import url_for

from converters1 import RegexConverter
from settings import Config

app = Flask(__name__)

# DEBUG
# 1.属性
# app.debug = True

# 2.config,是一个存储app所有配置的字典,Key都是大写
# app.config['DEBUG'] = True

# 3.加载文件,完整文件名
# app.config.from_pyfile('settings.py')

# 4,导包 加载对象(更为推荐)
app.config.from_object(Config)

@app.route('/')
def test():
    # return 'TESE!'
    return render_template('index.html')

# 定义多种可接受请求方式
@app.route('/methods',methods=['POST','GET'])
def method():
    return ('method')

# 查订单,传参
@app.route('/num/<int:num_id>')
def num(num_id):
    # return 'num_id = ',num_id + 'type:', type(num_id)
    print type(num_id)
    return ('num_id = %s' % num_id)

# 重定向
@app.route('/redirect')
def redirect_demo():
    return redirect(url_for('test'))


# 返回JSON数据
@app.route('/json')
def json_demo():
    dict = {
        'name':'xiaoxin',
        'age':5
    }
    # return json.dumps(dict),200,{'Content-Type': 'application/json'}
    return jsonify(dict)

# 添加到系统
app.url_map.converters['re']=RegexConverter
# 使用

# 自定义正则表达式,过滤路由
@app.route('/regex/<int(re(r"\d+")):num>')
def regex_converters(num):
    return 'num=%d'%num

if __name__ == '__main__':
    app.run(debug=True)