# -*- coding:utf-8 -*-
from flask import Flask,request

app = Flask(__name__)


@app.route('/',methods=['GET','POST'])
def hello_world():

    print 'method:%s'%request.method
    print 'headers:%s'%request.headers
    print 'url:%s'%request.url
    print 'cookies:%s'%request.cookies

    # args: name=XXX  form:name=XXX data=XXX file=图片
    print 'args: %s' % request.args.get()
    print 'data: %s' % request.data
    print 'files: %s' %  request.files
    print 'form: %s' % request.form.get('name')

    # 保存图片到当前目录
    # 需要设置当前项目的工作目录, 这样传入文件路径时, '.'就可以表示当前项目根目录
    img_file = request.files.get('image')
    img_file.save('./img.jpg')

    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
