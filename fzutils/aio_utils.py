# coding:utf-8

"""
aio 异步utils
"""

import re
from time import time
from gc import collect
from asyncio import get_event_loop, wait
from scrapy.selector import Selector

from .ip_pools import ip_proxy_pool, fz_ip_pool
from .spider.fz_aiohttp import AioHttp
from .common_utils import _print
from .spider.fz_requests import (
    Requests,
    PROXY_TYPE_HTTP,
    PROXY_TYPE_HTTPS,)
from .internet_utils import get_base_headers
from .spider.fz_driver import (
    BaseDriver,
    PC,
    PHANTOMJS,)
from .spider.fz_phantomjs import PHANTOMJS_DRIVER_PATH

__all__ = [
    'Asyncer',
    'get_async_execute_result',     # 获取异步执行结果
    'async_wait_tasks_finished',    # 异步等待目标tasks完成
    'TasksParamsListObj',           # 任务参数List
    'unblock_request',              # 非阻塞的request请求
    'unblock_get_driver_obj',       # 异步获取driver obj
    'unblock_request_by_driver',    # 非阻塞的request by driver
    'unblock_func',                 # 异步函数非阻塞
]

class Asyncer(object):
    '''异步类'''
    async def get_async_requests_body(**kwargs):
        return await AioHttp.aio_get_url_body(**kwargs)

def get_async_execute_result(obj=Asyncer,
                             obj_method_name='get_async_requests_body',
                             **kwargs):
    '''
    获取异步执行结果
    :param obj: 对象的类
    :param obj_method_name: 对象的方法名
    :param kwargs: 该方法附带的参数
    :return:
    '''
    loop = get_event_loop()
    if hasattr(obj, obj_method_name):
        method_callback = getattr(obj, obj_method_name)
    else:
        raise AttributeError('{obj}类没有{obj_method_name}方法!'.format(obj=obj, obj_method_name=obj_method_name))

    result = loop.run_until_complete(
        future=method_callback(**kwargs))

    return result

async def async_wait_tasks_finished(tasks:list) -> list:
    '''
    异步等待目标tasks完成
    :param tasks: 任务集
    :return:
    '''
    s_time = time()
    try:
        print('请耐心等待所有任务完成...')
        success_jobs, fail_jobs = await wait(tasks)
        print('执行完毕! success_task_num: {}, fail_task_num: {}'.format(len(success_jobs), len(fail_jobs)))
        time_consume = time() - s_time
        print('此次耗时 {} s!'.format(round(float(time_consume), 3)))
        all_res = [r.result() for r in success_jobs]
    except Exception as e:
        print(e)
        return []

    return all_res

class TasksParamsListObj(object):
    """
    任务参数List
        simple use:
            a = [1,2,3,4,5]
            _ = TasksParamsListObj(tasks_params_list=a, step=2)
            while True:
                try:
                    print(_.__next__())
                except AssertionError as e:
                    break
    """
    def __init__(self, tasks_params_list, step, slice_start_index=0):
        '''
        :param tasks_params_list: tasks 的参数list
        :param step: 步长，即并发量
        :param slice_start_index: 切片起始位置
        '''
        self.tasks_params_list = tasks_params_list
        self.tasks_params_list_len = len(tasks_params_list)
        self.step = step
        self.slice_start_index = slice_start_index

    def __next__(self):
        assert self.slice_start_index < self.tasks_params_list_len, '超出长度!'

        res = self.tasks_params_list[self.slice_start_index:self.step+self.slice_start_index]
        self.slice_start_index += self.step
        # print(self.slice_start_index)

        return res

    def __del__(self):
        try:
            del self.tasks_params_list
        except:
            pass
        collect()

async def unblock_request(url,
                          use_proxy=True,
                          headers:dict=get_base_headers(),
                          params=None,
                          data=None,
                          cookies=None,
                          had_referer=False,
                          encoding='utf-8',
                          method='get',
                          timeout=12,
                          num_retries=1,
                          high_conceal=True,
                          ip_pool_type=ip_proxy_pool,
                          verify=None,
                          _session=None,
                          get_session=False,
                          proxies=None,
                          proxy_type=PROXY_TYPE_HTTP,
                          logger=None) -> str:
    """
    非阻塞的request请求
    :param url:
    :param use_proxy:
    :param headers:
    :param params:
    :param data:
    :param cookies:
    :param had_referer:
    :param encoding:
    :param method:
    :param timeout:
    :param num_retries:
    :param high_conceal:
    :param ip_pool_type:
    :param verify:
    :param _session:
    :param get_session:
    :param proxies:
    :param proxy_type:
    :param logger:
    :return:
    """
    async def _get_args() -> list:
        """获取args"""
        return [
            url,
            use_proxy,
            headers,
            params,
            data,
            cookies,
            had_referer,
            encoding,
            method,
            timeout,
            num_retries,
            high_conceal,
            ip_pool_type,
            verify,
            _session,
            get_session,
            proxies,
            proxy_type,
        ]

    loop = get_event_loop()
    args = await _get_args()
    body = ''
    try:
        body = await loop.run_in_executor(None, Requests.get_url_body, *args)
    except Exception as e:
        _print(msg='遇到错误:', logger=logger, log_level=2, exception=e)
    finally:
        # loop.close()
        try:
            del loop
        except:
            pass
        collect()

        return body

async def unblock_get_driver_obj(type=PHANTOMJS,
                                 load_images=False,
                                 executable_path=PHANTOMJS_DRIVER_PATH,
                                 logger=None,
                                 high_conceal=True,
                                 headless=False,
                                 driver_use_proxy=True,
                                 user_agent_type=PC,
                                 driver_obj=None,
                                 ip_pool_type=ip_proxy_pool,
                                 extension_path=None,
                                 driver_cookies=None,):
    '''
    异步获取一个driver obj
    :return:
    '''
    async def _get_init_args() -> list:
        '''获取args'''
        return [
            type,
            load_images,
            executable_path,
            logger,
            high_conceal,
            headless,
            driver_use_proxy,
            user_agent_type,
            driver_obj,
            ip_pool_type,
            extension_path,
            driver_cookies,
        ]

    loop = get_event_loop()
    driver_args = await _get_init_args()
    try:
        driver_obj = await loop.run_in_executor(None, BaseDriver, *driver_args)
    except Exception as e:
        _print(msg='遇到错误:', logger=logger, log_level=2, exception=e)
    finally:
        # loop.close()
        try:
            del loop
        except:
            pass
        collect()

        return driver_obj

async def unblock_request_by_driver(url,
                                    type=PHANTOMJS,
                                    load_images=False,
                                    executable_path=PHANTOMJS_DRIVER_PATH,
                                    logger=None,
                                    high_conceal=True,
                                    headless=False,
                                    driver_use_proxy=True,
                                    user_agent_type=PC,
                                    driver_obj=None,
                                    ip_pool_type=ip_proxy_pool,
                                    extension_path=None,
                                    driver_cookies=None,

                                    css_selector='',
                                    exec_code='',
                                    timeout=20, ) -> str:
    '''
    非阻塞的driver 的请求
    :return:
    '''
    async def _get_request_args() -> list:
        return [
            url,
            css_selector,
            exec_code,
            timeout,
        ]

    loop = get_event_loop()
    body = ''
    request_args = await _get_request_args()
    try:
        driver = await unblock_get_driver_obj(
            type=type,
            load_images=load_images,
            executable_path=executable_path,
            logger=logger,
            high_conceal=high_conceal,
            headless=headless,
            driver_use_proxy=driver_use_proxy,
            user_agent_type=user_agent_type,
            driver_obj=driver_obj,
            ip_pool_type=ip_pool_type,
            extension_path=extension_path,
            driver_cookies=driver_cookies,)
        body = await loop.run_in_executor(None, driver.get_url_body, *request_args)
    except Exception as e:
        _print(msg='遇到错误:', logger=logger, log_level=2, exception=e)
    finally:
        # loop.close()
        try:
            del loop
        except:
            pass
        try:
            del driver
        except:
            pass
        collect()

        return body

async def unblock_func(func_name:object, func_args, logger=None, default_res=None):
    """
    异步函数非阻塞
    :param func_name: def 函数对象名
    :param func_args: 请求参数可迭代对象(必须遵循元素入参顺序!)
    :param logger:
    :param default_res: 默认返回结果
    :return:
    """
    loop = get_event_loop()
    try:
        default_res = await loop.run_in_executor(None, func_name, *func_args)
    except Exception as e:
        _print(msg='遇到错误:', logger=logger, log_level=2, exception=e)
    finally:
        # loop.close()
        try:
            del loop
        except:
            pass
        collect()

        return default_res
