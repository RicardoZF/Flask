# -*- coding:utf-8 -*-

def num(num1,num2):
    # 两数都是整数,num2不为0

    assert isinstance(num1,int),'num1 must is int'
    assert isinstance(num2,int),'num2 must is int'
    assert num2 != 0,'num2 not 0'

    print num1/num2


num(1,0)