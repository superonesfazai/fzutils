# coding:utf-8

'''
@author = super_fazai
@File    : gevent_utils.py
@connect : superonesfazai@gmail.com
'''

"""
gevent utils
"""

from gevent import sleep as gevent_sleep
from gevent import joinall as gevent_joinall
from gevent import Timeout as GeventTimeout
from gevent.pool import Pool as GeventPool
from gevent import monkey as gevent_monkey
from gevent import (
    Greenlet,
)

# 猴子补丁
# TODO 全部替换
# gevent_monkey.patch_all()
# TODO sql 连接只需针对socket连接的替换即可
# gevent_monkey.patch_socket()