# coding:utf-8

'''
@author = super_fazai
@File    : async_always.py
@connect : superonesfazai@gmail.com
'''

"""
预导入异步高并发爬虫常用的包

使用只需: from fzutils.spider.async_always import *
"""

import re
from time import sleep
from pprint import pprint
from scrapy.selector import Selector
from json import dumps, loads

from asyncio import (
    new_event_loop,
    get_event_loop,
    wait,
    Queue,                      # 一个队列，用于协调生产者和消费者协同程序。
    PriorityQueue,              # 子类Queue; 按优先级顺序检索条目(最低的第一个)
    LifoQueue,
    ensure_future,
    Semaphore,                  # 信号量实现
    Future,
    CancelledError,
    gather,                     # 返回给定协程对象或期货的未来聚合结果, 所有期货必须共享相同的事件循环
    iscoroutine,                # True如果obj是协程对象
    iscoroutinefunction,        # True如果确定func是协程函数
    run_coroutine_threadsafe,   # 将coroutine对象提交给给定的事件循环, 此函数旨在从与运行事件循环的线程不同的线程调用
    subprocess,
    shield,
    set_event_loop,
    Condition,                  # 该类实现条件变量对象。条件变量允许一个或多个协同程序等待，直到它们被另一个协程通知。
    as_completed,
    set_event_loop_policy,      # 修改事件循环规则
)
from asyncio import sleep as async_sleep
from asyncio import Lock as AsyncLock
from asyncio import TimeoutError as AsyncTimeoutError
# 原生超时设置
from asyncio import wait_for as async_wait_for
from uvloop import EventLoopPolicy
# with ThreadPoolExecutor(max_workers=10) as executor:
from concurrent.futures import ThreadPoolExecutor

from ..ip_pools import *
from ..internet_utils import *
from .fz_requests import Requests
from ..common_utils import *
from ..aio_utils import *
from ..time_utils import *
from ..js_utils import *
from ..sms_utils import *
from ..safe_utils import *
from .crawler import *
from ..linux_utils import *
from ..cp_utils import *
from ..url_utils import *
from ..img_utils import *
from ..map_utils import *
