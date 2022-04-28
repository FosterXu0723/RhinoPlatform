"""
@File:Api.py
@author:yangwuxie
@date: 2021/03/16
"""
import requests
from requests.exceptions import Timeout, InvalidURL, HTTPError


class Api(object):

    def __init__(self, method: str, url: str, params: dict, headers: dict):
        self.session = requests.session()
        self.apiMethod = method
        self.apiUrl = url
        self.apiParams = params
        self.apiHeaders = headers

    def execute(self) -> requests.Response:
        if self.apiMethod.upper() == "GET":
            try:
                response: requests.Response = self.session.get(url=self.apiUrl, params=self.apiParams,
                                                               headers=self.apiHeaders)
                return response
            except Timeout:
                return {"get请求出错": "请求超时"}
            except InvalidURL:
                return {"get请求出错": "非法的URl"}
            except HTTPError:
                return {"get请求出错": "http请求错误"}
            except Exception as e:
                return {"get请求出错": f"错误原因:{e}"}
        elif self.apiMethod.upper() == "POST":
            try:
                response: requests.Response = self.session.post(url=self.apiUrl, data=self.apiParams,
                                                                headers=self.apiHeaders)
                return response
            except Timeout:
                return {"post请求出错": "请求超时"}
            except InvalidURL:
                return {"post请求出错": "非法的URl"}
            except HTTPError:
                return {"post请求出错": "http请求错误"}
            except Exception as e:
                return {"post请求出错": f"错误原因:{e}"}
