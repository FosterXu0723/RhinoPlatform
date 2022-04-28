"""
@File: BaseResponse.py
@author: guoweiliang
@date: 2021/5/21
"""
from collections import namedtuple, defaultdict

FLASK_RESPONSE = defaultdict()


class BaseResponse():

    def __init__(self, code, msg, data, total=0, *args, **kwargs):
        """
        定义通用的响应内容
        :param code: 内部自定义接口响应码
        :param msg: 内部自定义接口响应内容
        :param data: 内部自定义接口响应体
        :param total: 返回的total
        """
        pass


class Result(BaseResponse):

    def __init__(self):
        pass

    @classmethod
    def success(cls, data, code=10000, msg="success"):
        prepare = defaultdict(list)
        for key, value in data:
            pass
        return defaultdict()

    @classmethod
    def failure(cls, data, code=99999, msg="failure"):
        return


