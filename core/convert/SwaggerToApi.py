"""
@File: SwaggerToApi.py
@author: guoweiliang
@date: 2021/11/23
"""
import time

from core.convert.tools import loadJsonFile
from error_message import FileTypeNotAllowed


class SwaggerFile(object):
    """

    """

    def __init__(self):
        pass


class SwaggerParser(object):
    """
    将swagger文件转成系统能够识别的
    """

    def __init__(self, fileName):
        self.file = fileName
        self.apiCollections = loadJsonFile(self.file)

    def getFile(self):
        return self._file

    def setFile(self, value: str) -> None:
        if not value.endswith('json'):
            raise FileTypeNotAllowed("文件不是json类型！")
        self._file = value

    file = property(getFile, setFile)

    def __makeRequestMethod(self, testApiDict, entryJson):
        """
        Args:
        {
            "query_path": {
            "path": "/sys/disableUser",
            "params": []
            },
            "edit_uid": 0,
            "status": "done",
            "type": "static",
            "req_body_is_json_schema": true,
            "res_body_is_json_schema": true,
            "api_opened": false,
            "index": 0,
            "tag": [],
            "_id": 24492,
            "res_body": "{\"type\":\"object\",\"properties\":{\"code\":{\"type\":\"integer\"},\"msg\":{\"type\":\"string\"},\"data\":{\"type\":\"object\",\"properties\":{}},\"success\":{\"type\":\"boolean\"}},\"$schema\":\"http://json-schema.org/draft-04/schema#\",\"description\":\"\"}",
            "method": "GET",
            "res_body_type": "json",
            "title": "禁用用户",
            "path": "/sys/disableUser",
            "catid": 5652,
            "markdown": "禁用用户",
            "req_headers": [],
            "req_query": [
            {
            "required": "0",
            "_id": "6110c7509a6a24072c10d32e",
            "name": "userId",
            "example": "0",
            "desc": ""
            }
            ],
            "desc": "<p>禁用用户</p>\n",
            "project_id": 291,
            "req_params": [],
            "uid": 226,
            "add_time": 1627956210,
            "up_time": 1628489552,
            "req_body_form": [],
            "__v": 0
        }
        构造请求方法
        :return:
        """
        pass

    def __makeRequestPath(self, testApiDict, entryJson):
        """
        构造请求路径
        :return:
        """
        pass

    def __makeRequestHeader(self):
        """
        构造请求头
        :return:
        """
        pass

    def __makeRequestBody(self):
        """
        构造请求体
        :return:
        """
        pass

    def __makeValidate(self):
        """
        构造断言
        :return:
        """
        pass

    def _prepareApi(self):
        apiDict = {"name": "", "request": {}, "validate": []}
        pass


if __name__ == '__main__':
    bb = SwaggerParser("/Users/guoweiliang/Downloads/api.json")

