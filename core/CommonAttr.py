"""
@File:CommonAttr.py
@author:yangwuxie
@date: 2021/01/05
"""
import importlib
import re
from typing import List

from app.models import TestStep, Interface
from app.utils.RequestParamsUtils import str2Dict
from common.Log import log
from core.ExternalFunction import getFunctionMapping
from error_message import TransferException, QueryException
from jsonpath import jsonpath

"""
处理参数
"""


class CommonAttr(object):
    _globalVar = {}

    def __init__(self, caseStep: TestStep):
        """
        初始化，有interface_id的时候去拿接口数据，没有接口直接拿当前step中的数据
        :param caseStep:
        """
        self.caseStep = caseStep
        log.info(f"入参case, id:{self.caseStep.id}, header: {self.caseStep.step_api_header}, "
                 f"data:{self.caseStep.step_api_data}, extract: {self.caseStep.step_api_extract}, "
                 f"ast: {self.caseStep.step_api_assert}")
        self.caseId = caseStep.id or None
        self.interfaceId = caseStep.interface_id
        if self.interfaceId:
            self._getApiData()
        else:
            self.header = str2Dict(caseStep.step_api_header) if not isinstance(caseStep.step_api_header, dict) else \
                caseStep.step_api_header
            self.path = caseStep.step_api_path or None
            self.method = caseStep.step_api_method or None
            self.data = str2Dict(caseStep.step_api_data) if not isinstance(caseStep.step_api_data, dict) else \
                caseStep.step_api_data
        self.extract = str2Dict(caseStep.step_api_extract) if not isinstance(caseStep.step_api_extract,
                                                                             dict) else caseStep.step_api_extract  # dict类型
        self.ast = str2Dict(caseStep.step_api_assert) if not isinstance(caseStep.step_api_assert, dict) else \
            caseStep.step_api_assert

    @property
    def globarVar(self):
        return self._globalVar

    @globarVar.setter
    def set(self, value: dict):
        self._globalVar.update(value)

    def _checkReplace(self, content):
        """
        判断存在占位符 ${}
        :return:
        """
        if not isinstance(content, str):
            try:
                if '${' in str(content):
                    return True
                else:
                    return False
            except Exception as e:
                raise TransferException("类型转换失败！")

    def doReplace(self, content):
        """
        替换参数处理，${test}
        :param content: 待处理参数 包含${}符号
        :return:
        """
        pattern = r'\$\{.*?\}'
        json_str = str(content)
        if not self._checkReplace(content):
            return content
        match_list = re.findall(pattern, json_str)
        if len(match_list) == 0:
            return eval(json_str)
        # if len(match_list) != len(dest.keys()):
        #     logger.warning("目标参数过多，请检查，dest：{}".format(dest))
        #     return eval(json_str)  # 直接返回，节省资源
        for match in match_list:
            is_change = False
            for key in CommonAttr._globalVar.keys():
                if is_change:
                    break
                dest_str_value = ""
                # 是否包含key
                if not match.__contains__(key):
                    continue
                # 判断是否为str，re.sub中需要参数str
                if not isinstance(CommonAttr._globalVar[key], str):
                    dest_str_value = str(CommonAttr._globalVar[key])
                else:
                    dest_str_value = CommonAttr._globalVar[key]
                json_str = re.sub(pattern, dest_str_value, json_str, 1)
                is_change = True
        log.info("【替换参数】参数列表为：{}".format(match_list))
        return eval(json_str)

    def doExtract(self, responseContent: dict, extractIndex=0):
        """
        后置处理 暂定self.extract为字典对象 key为储存变量名称 value为取出来的值
        :param responseContent: 响应内容
        :param extractIndex: 提取参数索引，默认提取第一个
        :return: None
        """
        if not self.extract:
            return
        else:
            if len(self.extract) == 0:
                return
        if not responseContent:
            return
        try:
            result = {}
            try:
                for key, value in self.extract.items():
                    # 返回匹配结果
                    matctCase = jsonpath(responseContent, value)
                    if matctCase:
                        pass
                    else:
                        continue  # 表示match_case为False
                    # 默认用第一个
                    result[key] = matctCase[extractIndex]
            except Exception as e:
                log.error(f"【程序运行出错】：{e}")
            # 更新全局变量字典
            self._globalVar.update(result)
            log.info("【更新全局变量】新增变量：{}".format(result))
            return result
        except Exception as e:
            log.error("【程序运行出错】：{}".format(e))

    def _getValue(self, responseContent, _, extractIndex):
        """
        获取value值
        :param responseContent: 原始内容str/dict
        :param _: 提取表达式
        :param extractIndex: 取值索引
        :return:
        """
        pass

    def _getApiData(self):
        """
        获取api参数
        :return:
        """
        try:
            interface = Interface.query.filter(Interface.id == self.interfaceId).first()
            self.header = interface.interface_headers
            self.path = interface.interface_url
            self.method = interface.interface_meth
            self.data = interface.interface_param
            try:
                self.extract = interface.extract or None
            except Exception:
                self.extract = self.caseStep.step_api_extract
        except Exception as e:
            log.error(f"查询失败：{e}")
            raise QueryException("查询失败！")

    def _isContainsFunc(self, content):
        """
        判断是否包含方法
        :param content:
        :return: Bool
        """
        if not isinstance(content, str):
            content = str(content)
        return True if re.search(r'\$.*?\)', content) else False

    def getFunctionArgs(self, content) -> List[List]:
        pattern = r'\$.*?\)'
        result = list()
        if not isinstance(content, str):
            content = str(content)
        match_list = re.findall(pattern, content)
        # 没有匹配上直接返回
        if not match_list:
            return None
        for match in match_list:
            start_index = str(match).index("(") + 1
            end_index = match.index(")")
            try:
                args = match[start_index:end_index]
                # 没有参数
                if not args:
                    # 写入空list
                    result.append(list())
                    continue
                split = args.split(",")
                # result.append(list(map(lambda x: int(x.strip()), split)))
                args_list = []
                for argument in split:
                    try:
                        args_list.append(int(argument))
                    except Exception as e:
                        args_list.append(str(argument))
                result.append(args_list)
                # todo 字典类型
            except Exception as e:
                pass
        return result

    def proccessExternalFunc(self, content):
        """
        执行外部函数
        :return:
        """
        pattern = r'\$\w+.*?\)'
        if isinstance(content, (list, tuple, dict)):
            content = str(content)
            args_list = self.getFunctionArgs(content)
            match_list = re.findall(pattern, content)
            # 获取方法名称和内存地址
            function_dict = getFunctionMapping(importlib.import_module('.ExternalFunction', package='core'))
            for index, match in enumerate(match_list):
                for func_name in function_dict.keys():
                    if match.__contains__(func_name):
                        if args_list[index]:
                            # 执行方法
                            function_result = function_dict[func_name](*args_list[index])
                        else:
                            # 没有参数直接执行
                            function_result = function_dict[func_name]()
                        if not isinstance(function_result, str):
                            function_result = str(function_result)
                        content = re.sub(pattern, function_result, content, 1)
                        log.info("【执行内部方法】方法名称：{},方法参数：{},方法结果：{}".format(func_name, args_list[index],
                                                                          function_result))
            return eval(content)
        elif isinstance(content, str):
            args_list = self.getFunctionArgs(content)
            match_list = re.findall(pattern, content)
            # 获取方法名称和内存地址
            function_dict = getFunctionMapping(importlib.import_module('ExternalFunction'))
            for index, match in enumerate(match_list):
                for func_name in function_dict.keys():
                    if match.__contains__(func_name):
                        # 执行方法
                        if args_list:
                            # 执行方法
                            function_result = function_dict[func_name](*args_list[index])
                        else:
                            # 没有参数直接执行
                            function_result = function_dict[func_name]()
                        if not isinstance(function_result, str):
                            function_result = str(function_result)
                        content = re.sub(pattern, function_result, content, 1)
                        log.info("【执行内部方法】方法名称：{},方法参数：{},方法结果：{}".format(func_name, args_list[index],
                                                                          function_result))
            return content
