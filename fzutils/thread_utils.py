# coding:utf-8

'''
@author = super_fazai
@File    : thread_utils.py
@connect : superonesfazai@gmail.com
'''

"""
thread utils
"""

from functools import wraps
from threading import (
    Thread,
)
from .common_utils import _print

__all__ = [
    'thread_safe',      # 线程安全装饰器
    'ThreadTaskObj',    # 重写任务线程
]

def thread_safe(lock):
    """
    线程安全装饰器
    :param lock: 锁
    :return:
    """
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper

    return decorate

class ThreadTaskObj(Thread):
    """
    重写任务线程
    """
    def __init__(self,
                 func_name,
                 args: (list, tuple)=(),
                 default_res=None,
                 logger=None):
        super(ThreadTaskObj, self).__init__()
        self.func_name = func_name
        self.args = args
        # Thread默认结果
        self.default_res = default_res
        self.res = default_res
        self.logger = logger

    def run(self):
        self.res = self.func_name(*self.args)

    def _get_result(self):
        try:
            # 等待线程执行完毕
            Thread.join(self)
            return self.res
        except Exception as e:
            _print(
                msg='线程遇到错误:',
                logger=self.logger,
                log_level=2,
                exception=e)

            return self.default_res