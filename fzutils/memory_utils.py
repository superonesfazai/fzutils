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

__all__ = [
    'memoizemethod_noargs',     # 使用一个方法缓存一个方法的结果（不带参数）弱引用对象
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
