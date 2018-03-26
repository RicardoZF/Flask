# -*- coding:utf-8 -*-
import time
from flask import Flask
from flask_mail import Mail,Message

app = Flask(__name__)

# 配置邮件：服务器／端口／安全套接字层／邮箱名／授权码
app.config['MAIL_SERVER'] = "smtp.qq.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "1370174361@qq.com"
app.config['MAIL_PASSWORD'] = "lvlyhoktzkmzgfab"
app.config['MAIL_DEFAULT_SENDER'] = 'FlaskAdmin<1370174361@qq.com>'

mail = Mail(app)


@app.route('/')
def hello_world():
    return '<a href="/send_mail">发送邮件</a>'

@app.route('/send_mail')
def send_mail():
    msg = Message('天高地迥,觉宇宙之无穷;兴尽悲来,识盈虚之有数',recipients=['1337418776@qq.com'],body='小猪佩奇身上纹,掌声送给社会人')
    # msg = Message('天高地迥,觉宇宙之无穷;兴尽悲来,识盈虚之有数',recipients=['1370174361@qq.com'],body='小猪佩奇身上纹,掌声送给社会人')
    while True:
        time.sleep(0.5)
        mail.send(msg)
    return 'send_mail'


if __name__ == '__main__':
    app.run(debug=True)