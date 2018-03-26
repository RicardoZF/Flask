# -*- coding:utf-8 -*-
from flask import Flask,render_template,request,flash

# 导入wtf扩展的表单类
from flask_wtf import FlaskForm

# 导入自定义表单需要的字段
from wtforms import SubmitField,StringField,PasswordField

#导入wtf扩展提供的表单验证器
from wtforms.validators import DataRequired,EqualTo

# 解决编码问题
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.secret_key = '666'

"""
使用WTF实现表单验证步骤
1. 自定义表单类 --> 继承FlaskForm
2. 在视图函数中, 创建该类, 并传入模板
3. 使用自己的方式实现表单的显示
"""
# 1. 自定义表单类 --> 继承FlaskForm
class LoginForm(FlaskForm):
    # <label>用户名:</label><input type="text" name="username" placeholder="请输入用户名"><br>
    username = StringField('用户名:',validators=[DataRequired()], render_kw={'placeholder':'请输入用户名'})
    password = PasswordField('密码:',validators=[DataRequired()],render_kw={'placeholder':'请输入密码'})
    password2 = PasswordField('确认密码:',validators=[DataRequired(),EqualTo('password','两次密码不一致')],render_kw={'placeholder':'请确认密码'})
    submit = SubmitField('提交')

@app.route('/form',methods=['POST','GET'])
def form():
    loginform = LoginForm()
    # 1,判断请求方式
    if request.method == 'POST':
        # 2. WTF可以一句话完成所有验证
        # 通过WTF也可以帮助我们补充忽略的一些安全的逻辑部分
        if loginform.validate_on_submit():
            return '验证成功'
        else:
            flash('验证失败')
    return render_template('index2.html',form=loginform)



@app.route('/',methods=['POST','GET'])
def index():
    # 1,判断请求,获取数据
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        password2=request.form.get('password2')
        # 2,校验数据
        if not all([username,password,password2]):
            flash ('参数不全')
        elif password != password2:
            flash ('密码不一致')
        else:
            return '验证成功'

    # 3,返回结果
    return render_template('index2.html')

if __name__ == '__main__':
    app.run(debug=True)