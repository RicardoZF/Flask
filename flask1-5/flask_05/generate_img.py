# -*- coding:utf-8 -*-
import json
import time
import urllib2

from flask import Flask

app = Flask(__name__)


APPID = 'wx21d659c4c87b4510'
APPSECRET = '7b6fc0fa5bc3b33309da4b562aed0c58'

class AccessToken(object):

    __access_token = {
        'access_token': '',
        'update_time': time.time(),
        'expires_in': 7200
    }

    @classmethod
    def get_access_token(cls):
        # 1. 是否存在  2. 是否过期 3. 返回token
        if not cls.__access_token.get('access_token') or \
                (time.time() - cls.__access_token.get('update_time') > cls.__access_token.get('expires_in')):

            # 获取数据

            url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (APPID, APPSECRET)

            response = urllib2.urlopen(url)

            resp_data = response.read()

            resp_dict = json.loads(resp_data)

            if 'errcode' in resp_dict:
                raise Exception(resp_dict.get('errmsg'))

            # 重新赋值
            cls.__access_token['access_token'] = resp_dict.get('access_token')
            cls.__access_token['expires_in'] = resp_dict.get('expires_in')
            cls.__access_token['update_time'] = time.time()

        # 返回token
        return cls.__access_token.get('access_token')


@app.route('/get_qrcode/<scene_id>')
def hello_world(scene_id):
    # 获取带参数的二维码的过程包括两步，首先创建二维码ticket，然后凭借ticket到指定URL换取二维码。
    # 1,发送请求, 获取ticket
    ticket_url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token='+ AccessToken.get_access_token()

    params = {"expire_seconds": 604800, "action_name": "QR_SCENE", "action_info": {"scene": {"scene_id": scene_id}}}
    # 使用urllib2发送POST请求
    response = urllib2.urlopen(ticket_url, data=json.dumps(params))

    # 获取返回的数据(字符串)
    resp_data = response.read()

    # 转化为字典
    resp_dict = json.loads(resp_data)

    # 2. 从字典中获取ticket
    ticket = resp_dict.get('ticket')

    # 3,到指定地址获取二维码图片
    img_url = 'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket='+ticket
    return '<img src=%s>' % img_url


if __name__ == '__main__':
    app.run(debug=True)