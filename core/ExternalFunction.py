"""
@File:ExternalFunction.py
@author:yangwuxie
@date: 2021/01/20
"""
import datetime
import json
import types
import time
import random
from typing import Dict

import faker
import requests

import config
from common.Log import log

"""
外部函数
"""
f = faker.Faker(locale='zh-CN')
token_cache = dict()
jwt_cache = dict()
jwt_cache_group=dict()


def getFunctionMapping(module: str) -> Dict:
    """
    获取方法名称：内存地址简化版
    >>> module = importlib.import_module("DataRandomUtils")
    >>> getFunctionMapping(module)
    {'get_token': <function get_token at 0x000001679FCD2C80>}
    :return:
    """
    return {name: item for name, item in vars(module).items() if isinstance(item, types.FunctionType)}


def get_token(mobile):
    """
    获取喂小保app token函数
    :param mobile:
    :return:
    """
    if mobile in token_cache.keys():
        return token_cache[mobile]
    # 调用获取登录验证码接口
    url1 = 'https://test.wxb.com.cn/substation/gateway/a/login/getAuthCode'
    requests.packages.urllib3.disable_warnings()
    rs1 = requests.post(url=url1, data={"mobile": mobile},
                        headers={"Content-Type": "application/x-www-form-urlencoded", "Ev": "v4"}, verify=False)
    if json.loads(rs1.text)['code'] == 10000 and json.loads(rs1.text)['msg'] == 'Success':
        # 调用登陆接口获取token
        try:
            url2 = 'https://test.wxb.com.cn/substation/gateway/a/login/doLogin'
            data2 = {'mobile': mobile, 'authCode': '1234', 'pCode': -1, 'deviceModel': 'Win32', 'channalId': '',
                     'version': '', 'osVersion': ''}
            requests.packages.urllib3.disable_warnings()
            rs2 = requests.post(url=url2, data=data2,
                                headers={"Content-Type": "application/x-www-form-urlencoded", "Ev": "v4"}, verify=False)
            tk = json.loads(rs2.text)['data']['token']
        except Exception as e:
            log.info(f"获取token失败:{e}")
    else:
        log.info("调用获取登录验证码接口失败")
    token_cache[mobile] = tk
    return tk


def get_jwt(username, password):
    """
    获取喂小保管理后台token
    :param username:
    :param password:
    :return:
    """
    if username in jwt_cache.keys():
        return jwt_cache[username]
    # 在喂小保后台调接口时,请求头需要用到jwt参数,此参数从登录接口中获取
    url = 'https://test.wxb.com.cn/dalaran/login'
    requests.packages.urllib3.disable_warnings()
    try:
        rs = requests.post(url=url, data={"userName": username, "pwd": password},
                           headers={"Content-Type": "application/x-www-form-urlencoded", "jwt": ""}, verify=False)
        if json.loads(rs.text)['code'] == 10000 and json.loads(rs.text)['msg'] == 'Success':
            jwt = json.loads(rs.text)['data']['jwt']
            jwt_cache[username] = jwt
            log.info(f"获取jwt:{jwt} 成功")
            return jwt
        else:
            log.info(f"{rs.text} 获取jwt失败")
    except Exception as e:
        log.error(f"调用获取jwt接口失败{e}")


def phoneGenerator():
    """
    随机生成电话号码
    :return:
    """
    return f.phone_number()


def nameGenerator():
    """
    随机生成姓名
    :return:
    """
    return f.name()


def fosun_batchno():
    """
    随机生成复兴批次号
    :return:
    """
    batchno = "test5020d31e0aa60b4" + str(random.randint(10000, 99999))
    return batchno


def fosun_applytime():
    """
    随机生成复兴承保时间
    :return:
    """
    applytime = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return applytime


def fosun_effectivedate():
    """
    随机生成复兴订单生效时间
    :return:
    """
    effectivedate = str(datetime.date.today() + datetime.timedelta(days=1)) + " " + "00:00:00"
    return effectivedate


def fosun_orderno():
    """
    随机生成复兴订单号
    :return:
    """
    orderno = "test4261723514" + str(random.randint(10000, 99999))
    return orderno


def get_app_host():
    """
    获取app host
    :return:
    """
    return config.APP_HOST


def generate_date(days, hours=0):
    """
    生成指定时间,可以调整小时
    :param days: 几天前or几天后。当天传0
    :return: 返回YmdHMS类型的时间
    """
    now_date = datetime.datetime.now()
    change_time = now_date + datetime.timedelta(days=days) + datetime.timedelta(hours=hours)
    return change_time.strftime("%Y-%m-%d %H:%M:%S")


def generate_short_date(days):
    """
    生成指定时间
    :param days: 几天前or几天后。当天传0
    :return: 返回Ymd类型的时间
    """
    now_date = datetime.datetime.now()
    change_time = now_date + datetime.timedelta(days=days)
    return change_time.strftime("%Y-%m-%d")


def generate_policyNo():
    """
    生成policy number
    :return:
    """
    policyno = "test0571" + str(random.randint(10000, 99999))
    return policyno


def fuson_order_new(order: str):
    """
    这是用来测试的方法，忽略
    :param order:
    :return:
    """
    return order.lstrip("test")


def get_timestamp(units):
    """
    获得时间戳方法
    units:多少位的时间戳
    t0:原始时间数据
    t1:转换后的时间戳数据
    """
    t0 = time.time()
    if units == 10:
        t1 = int(t0)
    elif units == 13:
        t1 = int(round(t0 * 1000))
    elif units == 16:
        t1 = int(round(t0 * 1000000))
    else:
        t1 = int(t0)
    return t1


def companyGenerator():
    """
    随机生成公司名
    :return:
    """
    return f.company()


def get_groupinsur_jwt(username1, password1):
    if username1 in jwt_cache_group.keys():
        return jwt_cache_group[username1]
    # 在企团险后台调接口时,请求头需要用到jwt参数,此参数从登录接口中获取
    url = 'https://test.wxb.com.cn/northrend/login'
    requests.packages.urllib3.disable_warnings()
    try:
        rs = requests.get(url, params={"userName": username1, "pwd": password1},
                          headers={"jwt": ""}, verify=False)
        if json.loads(rs.text)['code'] == 10000 and json.loads(rs.text)['msg'] == 'Success':
            jwt = json.loads(rs.text)['data']['jwt']
            jwt_cache_group[username1] = jwt
            # logger.info(f"获取jwt:{jwt} 成功")
            return jwt
        else:
            # logger.info(f"{rs.text} 获取jwt失败")
            pass
    except Exception as e:
        # logger.error(f"调用获取jwt接口失败{e}")
        pass
