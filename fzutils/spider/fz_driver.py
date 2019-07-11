# coding:utf-8

'''
@author = super_fazai
@File    : fz_driver.py
@connect : superonesfazai@gmail.com
'''

from .fz_phantomjs import (
    MyPhantomjs,
    CHROME,
    PHANTOMJS,
    FIREFOX,
    PC,
    PHONE,)
from .chrome_remote_interface import (
    ChromiumPuppeteer,
    PYPPETEER,
)
from .chrome_extensions import ChromeSwitchProxyExtensioner

__all__ = [
    'BaseDriver',
    'ChromiumPuppeteer',
    'ChromeSwitchProxyExtensioner',
]

class BaseDriver(MyPhantomjs):
    pass

