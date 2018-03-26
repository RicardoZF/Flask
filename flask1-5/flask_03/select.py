# -*- coding:utf-8 -*-
'''
'''

"""
1. 查询所有用户数据
User.query.all()


2. 查询有多少个用户
User.query.count()

3. 查询第1个用户
User.query.first()

4. 查询id为4的用户[3种方式]
User.query.filter(User.id==4).first()
User.query.get(4)
User.query.filter_by(id = 4).first()

5. 查询名字结尾字符为g的所有数据[开始/包含]
 User.query.filter(User.name.endswith('g')).all()

6. 查询名字不等于wang的所有数据[2种方式]
User.query.filter(User.name != 'wang').all()
User.query.filter(not_(User.name == 'wang')).all()

7. 查询名字和邮箱都以 li 开头的所有数据[2种方式]
User.query.filter(User.name.startswith('li'),User.email.startswith('li')).all()
User.query.filter(and_(User.name.startswith('li'),User.email.startswith('li'))).all()


8. 查询password是 `123456` 或者 `email` 以 `itheima.com` 结尾的所有数据
User.query.filter(or_(User.password=='123456',User.email.endswith('itheima.com'))).all()

9. 查询id为 [1, 3, 5, 7, 9] 的用户列表
User.query.filter(User.id.in_([1, 3, 5, 7, 9])).all()

10. 查询name为liu的角色数据
User.query.filter(User.name=='liu').first().role

11. 查询所有用户数据，并以邮箱排序
User.query.order_by(User.email).all()

12. 查询第2页的数据, 每页只显示3条数据

paginate 需要3个参数( 第几页, 分页的数量条件, 如果失败了是否要返回404错误 )
data.items 获取所有的查询数据
data.page 获取当前页数
data.pages 获取总页数

result = User.query.paginate(2,3,False)
result.items

"""