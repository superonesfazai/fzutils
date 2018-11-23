# coding:utf-8

"""
aio 异步utils
"""

import re
from time import time
from gc import collect
from asyncio import get_event_loop, wait
from scrapy.selector import Selector

from .spider.fz_aiohttp import AioHttp
from .common_utils import _print

__all__ = [
    'Asyncer',
    'get_async_execute_result',     # 获取异步执行结果
    'async_wait_tasks_finished',    # 异步等待目标tasks完成
    'TasksParamsListObj',           # 任务参数List
    '_parse_field',                 # 异步根据类型解析字段
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

async def _parse_field(parser: dict,
                       target_obj: (str, dict),
                       re_is_first=True,
                       logger=None) -> (str, list):
    '''
    ** 异步根据类型解析字段
    :param parser: 解析对象 eg: {'method': 'css', 'selector': '.sss'}
    :param target_obj: 待处理的目标对象
    :param re_is_first: bool 是否re只提取第一个
    :return:
    '''
    res = ''
    if parser is not None:
        parser_method = parser.get('method', '')
        parser_selector = parser.get('selector')
        if parser_method == 're':
            try:
                _ = re.compile(parser_selector).findall(target_obj)
                if re_is_first: res = _[0]
                else: res = _
            except IndexError as e:
                _print(msg='遇到错误:', logger=logger, log_level=2, exception=e)

        elif parser_method == 'css':
            res = Selector(text=target_obj).css(parser_selector).extract_first() or ''

        elif parser_method == 'xpath':
            res = Selector(text=target_obj).xpath(parser_selector).extract_first() or ''

        elif parser_method == 'dict_path':
            # print(parser_selector)
            res = parser_selector

        else:
            raise ValueError('解析该字段的method值未知!')

    return res