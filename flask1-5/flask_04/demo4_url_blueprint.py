# -*- coding:utf-8 -*-
from flask import Flask
from hm_cart import app_cart

app = Flask(__name__)
app.register_blueprint(app_cart)

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)