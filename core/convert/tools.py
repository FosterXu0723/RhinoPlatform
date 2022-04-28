"""
@File: tools.py
@author: guoweiliang
@date: 2021/11/24
"""
import json
import sys
from itertools import chain, product, cycle
from json import JSONDecodeError
from typing import List, Generator


def loadJsonFile(fileName: str) -> Generator:
    """
    读取swagger.json内容
    :param fileName:
    :return: 返回api内容的生成器
    """
    with open(fileName, mode="rb") as f:
        try:
            loadJson = json.load(f)
            return (api for collection in loadJson for api in collection['list'])
        except (TypeError, JSONDecodeError) as ex:
            sys.exit(1)
        except KeyError:
            sys.exit(1)


def encodeXWWWFormHeader(postData: dict) -> dict:
    """
    req_headers content-type默认为application/json
    Args:
        'req_headers':
            [
                {'required': '1',
                '_id': '6110c7509a6a24072c10d32f',
                'name': 'jwt',
                'value': 'eyJhbGciOiJTSEE1MTIiLCJ0eXBlIjoiand0In0=.=.'}
            ]
    :param postData:
    :return:
    """
    headers = postData.get("req_headers")
    if headers.get("name") == "Content-Type":
        return {"Content-Type": headers.get("value")}
    else:
        return {"jwt": "", "Content-Type": "application/x-www-form-urlencoded"}


def convertRequestDataToDict(postData: dict) -> list:
    """
    获取请求参数
    :param postData:
    :return:
    """
    return [item.get("name") for item in postData.get("req_query")]


if __name__ == '__main__':
    jfile = loadJsonFile("/Users/guoweiliang/Downloads/api.json")
    for x in jfile:
        print(x)
