# coding:utf-8

'''
@author = super_fazai
@File    : memory_utils.py
@connect : superonesfazai@gmail.com
'''

"""
memory utils
"""

from weakref import WeakKeyDictionary
from functools import wraps
from inspect import stack as inspect_stack

from .common_utils import _print
# from fzutils.common_utils import _print

__all__ = [
    'memoizemethod_noargs',                                     # 使用一个方法缓存一个方法的结果（不带参数）弱引用对象
    'get_current_func_name',                                    # 获取当前被调用的函数名
]

def memoizemethod_noargs(method):
    '''
    使用一个方法缓存一个方法的结果（不带参数）弱引用对象
    :param method:
    :return:
    '''
    cache = WeakKeyDictionary()

    @wraps(method)
    def new_method(self, *args, **kwargs):
        if self not in cache:
            cache[self] = method(self, *args, **kwargs)

        return cache[self]

    return new_method

def get_current_func_name():
    """
    获取当前被调用的函数名
    eg:
    class MyClass:
        def function_one(self):
            print("%s.%s invoked" % (self.__class__.__name__, get_current_function_name()))
    a = MyClass()
    a.function_one()
    :return:
    """
    return inspect_stack()[1][3]