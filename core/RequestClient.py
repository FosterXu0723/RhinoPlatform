"""
@File:RequestClient.py
@author:yangwuxie
@date: 2021/01/04
"""
import requests
import operator
from core.CommonAttr import CommonAttr
from enum import Enum
import json
from common.Log import log
import aiohttp

from error_message import ParameterTypeOfDictException, RequestFailException

"""
处理请求
"""


class ContentTypeEnum(Enum):
    Raw = "application/json"

    FORM_DATA = "application/x-www-form-urlencoded"


class Client(CommonAttr):

    def __init__(self, testStep):
        self.session = requests.session()
        super().__init__(testStep)

    def get(self, url: str, params: dict, header: dict) -> requests.Response:
        # 先判断存在
        if params and not isinstance(params, dict):
            raise ParameterTypeOfDictException("请求参数不是字典类型！")
        try:
            r = self.session.get(url=url, params=params, headers=header, verify=False)
            return r
        except Exception as e:
            import traceback
            log.error(f"请求出错:{traceback.format_exc()}")
            raise RequestFailException(f"请求失败{e}")

    def post(self, url: str, params: dict, header: dict) -> requests.Response:
        if operator.contains(header, "Content-Type"):
            contentType = header.get('Content-Type')
            if operator.eq(contentType, ContentTypeEnum.Raw.value):
                try:
                    res = self.session.post(url=url, json=params, headers=header, verify=False)
                    return res
                except Exception as e:
                    log.error(f"接口请求出错:{e}")
                    raise RequestFailException(f"请求失败{e}")
            else:
                try:
                    res = requests.post(url=url, data=params, headers=header, verify=False)
                    return res
                except Exception as e:
                    log.error(f"接口请求出错:{e}")
                    raise RequestFailException(f"请求失败{e}")
        else:
            try:
                res = requests.post(url=url, data=params, headers=header, verify=False)
                return res
            except Exception as e:
                log.error(f"接口请求出错:{e}")
    # todo
    def retry(self):
        pass


async def get(client) -> aiohttp.ClientResponse:
    async with client.request(method="get", url='https://www.baidu.com', verify_ssl=False) as response:
        return await response.text()


async def requestProxy():
    async with aiohttp.ClientSession() as f:
        html = await get(f)
        print(html)


if __name__ == '__main__':
    import pytest
    print(Client().get(url="https://www.baidu.com", params={}, header={}))
