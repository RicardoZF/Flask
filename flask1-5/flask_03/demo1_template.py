# -*- coding:utf-8 -*-
from flask import Flask,render_template
from flask import flash
from flask import g
from flask import session

app = Flask(__name__)
app.secret_key = '666'

@app.route('/')
def hello_world():
    # g变量只能用于一次请求
    g.name = 'heima'
    return render_template('index1.html')

@app.route('/g_demo')
def g_demo():
    print g.name
    return 'g.name'

@app.route('/session_demo')
def session_demo():
    session['name'] = 'xiaoxin'
    return 'session'

@app.route('/order_demo/<int:order_id>')
def order_demo(order_id):
    return 'order_id: %s' % order_id
@app.route('/flash_demo')
def flash_demo():
    flash('666')
    return 'flash'

if __name__ == '__main__':
    app.run(debug=True)
