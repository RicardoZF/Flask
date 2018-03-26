# -*- coding:utf-8 -*-
from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def filter():
    list = [1,2,3,4,5]
    return render_template('filter.html',list = list)

# 方式一: add_template_filter方法实现自定义过滤器。一参函数名，二参是自定义的过滤器名
# def do_list_reverse(list):
#     list.reverse()
#     return list
#
# app.add_template_filter(do_list_reverse,'myreverse')

# 方式二:@app.template_filter(),传入的参数是自定义的过滤器名称。
@app.template_filter('myreverse')
def do_list_reverse(list):
    list.reverse()
    return list



if __name__ == '__main__':
    app.run(debug=True)