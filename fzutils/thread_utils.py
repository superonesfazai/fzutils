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
from pprint import pprint
from threading import (
    Thread,
)
from .common_utils import _print

__all__ = [
    'thread_safe',                                      # 线程安全装饰器
    'ThreadTaskObj',                                    # 重写任务线程
    'start_thread_tasks_and_get_thread_tasks_res',      # 开启线程任务集合病获取目标任务集合所有执行结果
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
    def __init__(self,
                 func_name,
                 args: (list, tuple)=(),
                 default_res=None,
                 func_timeout=None,
                 logger=None):
        """
        重写任务线程
        :param func_name:
        :param args:
        :param default_res:
        :param func_timeout: 超时时长, 单位秒
        :param logger:
        """
        super(ThreadTaskObj, self).__init__()
        self.func_name = func_name
        self.args = args
        # Thread默认结果
        self.default_res = default_res
        self.res = default_res
        self.func_timeout = func_timeout
        self.logger = logger

    def run(self):
        self.res = self.func_name(*self.args)

    def _get_result(self):
        try:
            # 等待线程执行完毕
            Thread.join(self, timeout=self.func_timeout)
            return self.res
        except Exception as e:
            _print(
                msg='线程遇到错误:',
                logger=self.logger,
                log_level=2,
                exception=e)

            return self.default_res

def start_thread_tasks_and_get_thread_tasks_res(tasks: list, logger=None) -> list:
    """
    开启线程任务集合病获取目标任务集合所有执行结果
    simple use:
        def do_something(index):
            return 'xxx'

        tasks = []
        for index in range(1, 100):
            print('create task[where is index: {}] ...'.format(index))
            task = ThreadTaskObj(
                func_name=do_something,
                args=[
                    index,
                ],
                default_res=None,
                func_timeout=None,)
            tasks.append(task)
        one_res = start_thread_tasks_and_get_thread_tasks_res(tasks=tasks)

    :param tasks:
    :param logger:
    :return:
    """
    from time import time

    s_time = time()
    one_res = []
    try:
        _print(msg='请耐心等待所有任务完成...', logger=logger,)

        # 同时开启每个线程
        for task in tasks:
            try:
                task.start()
            except Exception as e:
                _print(
                    msg='开启线程出错:',
                    logger=logger,
                    log_level=2,
                    exception=e)
                continue

        # 获取所有线程的执行结果
        for task in tasks:
            res = task._get_result()
            one_res.append(res)
        # pprint(one_res)

        _print(msg='此次耗时 {} s!'.format(round(float(time() - s_time), 3)), logger=logger)

    except Exception as e:
        _print(msg='遇到错误:', logger=logger, log_level=2, exception=e)
        return one_res

    return one_res