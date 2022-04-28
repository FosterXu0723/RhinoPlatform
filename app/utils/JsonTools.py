"""
@File: JsonTools.py
@author: yangwuxie
@date: 2021/4/12
"""
import importlib
import json
import types
from collections import OrderedDict
from typing import Dict

from core.ExternalFunction import companyGenerator


def unest(data, key):
    """
    深层遍历dict
    :param data:
    :param key:
    :return:
    """
    if key in data.keys():
        return data.get(key)
    else:
        for dkey in data.keys():
            if isinstance(data.get(dkey), dict):
                return unest(data.get(dkey), key)
            elif isinstance(data.get(dkey), list):
                while True:
                    try:
                        innerDict = next(iter(data.get(dkey)))
                        return unest(innerDict, key)
                    except StopIteration:
                        break

            else:
                continue


def parseInstance(obj) -> None:
    """
    处理db.Model的blob对象，让其先执行完存入的代码对象之后再返回前端
    当db.Column声明的是Datetime类型的时候，存入数据库的内容实际为datetime.datetime(******)，未执行的时候取出来的就是当前的datetime对象
    :param obj:
    :return:
    """
    attrDict = OrderedDict()
    for key, value in vars(obj).items():
        if not str(key).startswith("_"):
            attrDict[key] = value
    for attrKey, attrValue in vars(obj).items():
        if hasattr(obj, attrKey):
            setattr(obj, attrKey, attrValue)


def getApiLogContent(file_path) -> object:
    """
    获取日志文件中的API请求内容
    file_path: ../logs/platform.log
    获取最后一次 execute start 和execute end之间的日志内容
    :param file_path: 文件路径
    :return: log content
    """
    with open(file_path, "r", encoding="utf8") as file:
        lines = file.readlines()
        logContent = []
        lines.sort(reverse=True)
        recordFlag = False
        for line in lines:
            if "execute end" in line:
                # 表示接口请求日志已经开始
                recordFlag = True
                continue
            if recordFlag:
                logContent.append(line)
            if "execute start" in line:
                recordFlag = False
                break
        return sorted(logContent)


def getExternalFunctionDescMap() -> Dict[str, str]:
    """
    获取core.ExternalFunction.py下面函数和函数描述的字典
    :return: 函数名称：函数描述
    """
    pkg = importlib.import_module(".ExternalFunction", package="core")

    def sampleStr(content: str):
        return content[
               content.index(r"\n") + 2:content.index(
                   r"\n")].strip() if content is not None and r"\n" in content else ""

    return {name: item.__doc__.replace("\n", "") for name, item in vars(pkg).items() if
            isinstance(item, types.FunctionType)}


if __name__ == '__main__':
    print(getExternalFunctionDescMap())
