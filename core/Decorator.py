"""
@File: Decorator.py
@author: guoweiliang
@date: 2021/6/17
"""
import traceback
from functools import wraps
from inspect import signature

from common.Log import log

"""
各种装饰器
"""


def typeAssert(*tyArgs, **tyKwargs):
    """
    类型判断
    :param tyArgs:
    :param tyKwargs:
    :return:
    """

    def decorator(func):
        sig = signature(func)
        boundTypes = sig.bind_partial(*tyArgs, **tyKwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bindValue = sig.bind(*args, **kwargs)
            for name, value in bindValue.arguments.items():
                if name in boundTypes:
                    if not isinstance(value, boundTypes[name]):
                        raise TypeError("argument {} must be {} ".format(name, boundTypes[name]))
            return func(*args, **kwargs)

        return wrapper

    return decorator


def logError(func):
    """
    记录error
    :param func:
    :return:
    """
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except:
            log.error(str(traceback.format_exc()))

    return inner


