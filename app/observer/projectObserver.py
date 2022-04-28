"""
@File:projectObserver.py
@author:yangwuxie
@date: 2020/12/25
"""

from . import mySignal

# 自定义信号
deleteApi = mySignal.signal("deleteApi")


# 定义订阅者
@deleteApi.connect
def apiDeleteObserver(sender, **extra):
    print('in the api delete observer{}'.format(sender))


@deleteApi.connect
def testdemo(sender, **extra):
    print(f'in the testdemo observer{sender},{extra}')
