# -*- coding:utf-8 -*-

from flask import Flask,make_response,request,session
from flask import redirect
from flask import url_for

app = Flask(__name__)

@app.route('/')
def set_cookie():
    res = make_response('set cookie')
    res.set_cookie('name','xiaobai',max_age=3600)
    return res

@app.route('/get')
def get_cookie():
    cookie = request.cookies.get('name')
    return cookie

# 记得设置secret_key: app.secret_key = 'xxx'
app.secret_key='xiaobai'

@app.route('/set_session')
def set_session():
    session['username']='xiaoxin'
    return redirect(url_for('get_session'))

@app.route('/get_session')
def get_session():
    return session.get('username')


if __name__ == '__main__':
    app.run(debug=True)