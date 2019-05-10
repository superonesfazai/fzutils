# coding:utf-8

'''
@author = super_fazai
@File    : my_exceptions.py
@connect : superonesfazai@gmail.com
'''

__all__ = [
    'ResponseBodyIsNullStrException',       # 请求的应答返回的body为空str异常, 多用于处理proxy异常中, 避免数据误删
    'NoNextPageException',                  # 没有后续页面的异常
    'AppNoResponseException',               # app 长期运行, 无响应异常!
]

class ResponseBodyIsNullStrException(Exception):
    """请求的应答返回的body为空str异常, 多用于处理proxy异常中, 避免数据误删"""
    pass

class NoNextPageException(Exception):
    """没有后续页面的异常"""
    pass

class AppNoResponseException(Exception):
    """app 长期运行, 无响应异常!"""
    pass