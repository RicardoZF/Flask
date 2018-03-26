# -*- coding:utf-8 -*-
import hashlib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import xmltodict
from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/wechat8029',methods=['GET','POST'])
def wechat():
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    echostr = request.args.get('echostr')
    signature = request.args.get('signature')
    token = 'token'

    # 将token,timestamp,nonce三个参数进行字典排序
    list = [token,timestamp,nonce]
    list.sort()

    # 将三个参数拼接为一个字符串进行shal加密
    str = ''.join(list)
    sign = hashlib.sha1(str).hexdigest()

    # 开发者获得加密后的字符与signature对比,标示该请求来源于微信
    if signature == sign:
        # 对比成功,返回echostr标示与微信连通,说明是微信发来的数据
        # 利用了Token来加密,只有Token一直才说明是维系发来的
        if request.method == 'GET':
            return echostr
        if request.method == 'POST':
            """
            1,说什么回什么
            """
            # print request.data

            xml_dict = xmltodict.parse(request.data).get('xml')
            msg_type = xml_dict['MsgType']

            if msg_type == 'text':
                # 接受文字
                content = xml_dict.get('Content')
                print xml_dict['Content']

            elif msg_type == 'voice':
                # 接收语音
                content = xml_dict.get('Recognition')
            elif msg_type == 'event':
                # 订阅/取消订阅
                event = xml_dict.get('Event')
                if event == 'subscribe':
                    print '吴彦祖关注了公众号'
                    content = '吴彦祖,你帅气得关注了该公众号'
                    if xml_dict['EventKey']:
                        # 如果有EventKey,说明扫描了带参数的二维码
                        print '扫描了带参数的二维码'
                        content = '被吴彦祖关注了;场景值是:%s' % xml_dict.get('EventKey')

                elif event == 'unsubscribe':
                    print '吴彦祖取消了订阅'
                    content = None
                else:
                    print '其他订阅状态'
                    content = None
            else:
                print request.data
                content = '再见吧'

            resp = {
                'ToUserName': xml_dict.get('FromUserName'),
                'FromUserName': xml_dict.get('ToUserName'),
                'CreateTime': time.time(),
                'MsgType': 'text',
                'Content': content,
                # 'Content':'表清包',
            }

            # 拼接xml节点
            resp = {'xml': resp}
            # 将字典转换为xml返回
            return xmltodict.unparse(resp)

    return ''


if __name__ == '__main__':
    app.run(debug=True,port=8029)
