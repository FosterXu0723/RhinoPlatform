"""
@File:__init__.py.py
@author:yangwuxie
@date: 2020/12/25
"""
import types
from collections import namedtuple
import os
from app import db
from functools import wraps

from common.Log import log

BASEPATH = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


def notEmpty(*content):
    """
    判断内容是否为空
    :param content: 判断内容
    :return: 为空返回False，不为空返回True
    """
    if isinstance(content, (list, tuple)):
        filter_result = list(filter(lambda x: not x or x == "", content))
        if len(filter_result) == 0:
            return True
        else:
            return False
    return False if not content or content == "" else True


def equals(objA, objB):
    return True if objA == objB else False


def getChangeApply(modelObject: db.Model, paramsJson: dict) -> None:
    """
    获取有变更的属性值，批量更改
    :param modelObject: 表模型对象
    :param paramsJson: 请求参数json对象
    :return: None
    """
    for key in paramsJson.keys():
        if hasattr(modelObject, key):
            if equals(getattr(modelObject, key), paramsJson.get(key)):
                continue
            else:
                setattr(modelObject, key, paramsJson.get(key))
        else:
            continue


FuncArgs = namedtuple('FuncArgs', ('args', 'defaults'))


class FuncParser:

    @classmethod
    def parse_vars(cls, func):
        code = func.__code__
        argc = code.co_argcount
        kwargc = code.co_kwonlyargcount
        varnames = code.co_varnames

        res = {
            "arg": varnames[:argc],
            "kwarg": varnames[argc:argc + kwargc],
            "*args": None,
            "**kwargs": None
        }
        flag = code.co_flags
        if flag & 0x04:
            # Use *args
            res['*args'] = varnames[argc + kwargc]
        if flag & 0x08:
            # Use **kwargs
            res['**kwargs'] = varnames[argc + kwargc + bool(flag & 0x04)]

        # parse defaults
        defaults = func.__defaults__ or ()
        defaults_map = dict(zip(reversed(res['arg']), reversed(defaults)))
        defaults_map.update(func.__kwdefaults__ or {})
        return FuncArgs(res, defaults_map)

    @classmethod
    def build_param_str(cls, func_args):
        func_vars, defaults_map = func_args
        params = []
        # arg
        for arg in func_vars['arg']:
            if arg in defaults_map:
                default_val = defaults_map[arg]
                params.append(f'{arg}={default_val}')
            else:
                params.append(arg)

        # *args
        if func_vars['*args']:
            params.append(f"*{func_vars['*args']}")
        else:
            if func_vars['kwarg']:
                params.append('*')

        # kwarg
        for kwarg in func_vars['kwarg']:
            if kwarg in defaults_map:
                default_val = defaults_map[kwarg]
                params.append(f'{kwarg}={default_val}')
            else:
                # 一种函数定义不会遇到的情况，但在后面会用到它
                params.append(f'{kwarg}={kwarg}')

        # **kwargs
        if func_vars['**kwargs']:
            params.append(f"**{func_vars['**kwargs']}")

        param = ', '.join(params)
        param_str = '({})'.format(param)
        return param_str

    @classmethod
    def analyse_func_param(cls, func):
        func_args = cls.parse_vars(func)
        name = func.__name__
        return cls.build_param_str(func_args)


def nb_partial(*partial_args):
    """
    生成一个偏函数，且新函数的参数列表中会去除
    """

    def decorator(func):
        pre_arg_str = ', '.join(map(repr, partial_args))

        code = func.__code__
        if len(partial_args) > code.co_argcount:
            raise TypeError("Too many positional arguments")

        args = code.co_varnames[:code.co_argcount]
        post_args = args[len(partial_args):]
        post_args_str = ', '.join(post_args)

        func_def = (f"def wrapped({post_args_str}):\n"
                    f"    return func({pre_arg_str}, {post_args_str})")
        module_code = compile(func_def, '<>', 'exec')
        function_code = next(code for code in module_code.co_consts
                             if isinstance(code, types.CodeType))
        wrapped = types.FunctionType(function_code,
                                     {'func': func})
        return wraps(func)(wrapped)

    return decorator


class Node(object):

    def __init__(self, data=None, next=None):
        self.data = data
        self.next = next

    def __str__(self):
        return str(self.data)


class LinkedList(object):

    def __init__(self, head=None):
        self.head = head

    def __len__(self):
        curr = self.head
        counter = 0
        while curr is not None:
            counter += 1
            curr = curr.next
        return counter

    def insert_to_front(self, data):
        if data is None:
            return
        node = Node(data, self.head)
        self.head = node
        return node

    def append(self, data):
        if data is None:
            return
        node = Node(data)
        if self.head is None:
            self.head = node
            return node
        current_node = self.head
        while current_node.next is not None:
            current_node = current_node.next
        current_node.next = node
        return node

    def find(self, data):
        if data is None:
            return
        current_node = self.head
        while current_node is not None:
            if current_node.data == data:
                return current_node
            current_node = current_node.next
        return None

    def delete(self, data):
        """

        :param data:
        :return:
        """
        if data is None:
            return
        if self.head is None:
            return
        if self.head.data == data:
            self.head = self.head.next
            return
        pre_node = self.head
        current_node = self.head.next
        while current_node is not None:
            if current_node.data == data:
                pre_node.next = current_node.next
            else:
                pre_node = current_node
                current_node = current_node.next

    def delete_copy(self, data):
        if data is None:
            return
        if self.head is None:
            return
        if self.head.data == data:
            self.head = self.head.next
        cur_node = self.head
        while cur_node.next is not None:
            if cur_node.next.data == data:
                cur_node.next = cur_node.next.next
            cur_node = cur_node.next

    def __str__(self):
        result = []
        while self.head is not None:
            result.append(self.head.data)
            self.head = self.head.next
        return "".join(map(lambda x: str(x) + " ", result))


if __name__ == '__main__':
    print(os.path.join(BASEPATH, "logs/platform.log"))
