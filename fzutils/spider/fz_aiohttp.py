# coding:utf-8

'''
@author = super_fazai
@File    : fz_aiohttp.py
@Time    : 2017/7/14 14:45
@connect : superonesfazai@gmail.com
'''

import asyncio
import aiohttp
import re
import gc

from asyncio import get_event_loop
from gc import collect

from ..ip_pools import (
    MyIpPools,
    ip_proxy_pool,
    fz_ip_pool,)
from ..internet_utils import get_random_pc_ua

__all__ = [
    'MyAiohttp',
    'AioHttp',
]

class MyAiohttp(object):
    def __init__(self, ip_pool_type=ip_proxy_pool, max_tasks=10):
        super(MyAiohttp, self).__init__()
        self.loop = asyncio.get_event_loop()
        self.max_tasks = max_tasks                  # 接口请求进程数
        self.queue = asyncio.Queue(loop=self.loop)  # 接口队列
        self.ip_pool_type = ip_pool_type

    @property
    def headers(self):
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            # 'Accept-Encoding:': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'superonesfazai.github.io',
            'User-Agent': get_random_pc_ua(),
        }

    @classmethod
    async def aio_get_url_body(cls,
                               url,
                               headers,
                               method='get',
                               params=None,
                               timeout=10,
                               num_retries=10,
                               high_conceal=True,
                               data=None,
                               ip_pool_type=ip_proxy_pool,
                               verify_ssl=True,
                               use_dns_cache=True,
                               proxy_auth=None,
                               allow_redirects=True,
                               proxy_headers=None,):
        '''
        异步获取url的body(简略版)
        # 注意timeout不是越长越好，测试发现10左右成功率较高
        :param url:
        :param headers:
        :param params:
        :param had_proxy:
        :param num_retries: 出错重试次数
        :param hign_conceal: ip是否高匿
        :param data: post的data
        :return:
        '''
        proxy = await cls.get_proxy(ip_pool_type=ip_pool_type, high_conceal=high_conceal,)
        # print(proxy)
        if isinstance(proxy, bool):
            if proxy is False:
                print('异步获取代理失败! return ""!')
                return ''

        # 连接池不能太大, < 500
        conn = aiohttp.TCPConnector(
            verify_ssl=verify_ssl,
            limit=150,
            use_dns_cache=use_dns_cache,)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                async with session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        data=data,
                        proxy=proxy,
                        timeout=timeout,
                        proxy_auth=proxy_auth,
                        allow_redirects=allow_redirects,
                        proxy_headers=proxy_headers, ) as r:
                    # print(r)
                    result = await r.text(encoding=None)
                    result = await cls.wash_html(result)
                    # print('success')
                    return result
            except Exception as e:
                # print('出错:', e)
                if num_retries > 0:
                    # 如果不是200就重试，每次递减重试次数
                    return await cls.aio_get_url_body(
                        url=url,
                        headers=headers,
                        method=method,
                        params=params,
                        timeout=timeout,
                        num_retries=num_retries-1,
                        high_conceal=high_conceal,
                        data=data,
                        ip_pool_type=ip_pool_type,
                        verify_ssl=verify_ssl,
                        use_dns_cache=use_dns_cache,
                        proxy_auth=proxy_auth,
                        allow_redirects=allow_redirects,
                        proxy_headers=proxy_headers,)
                else:
                    print('异步获取body失败!')
                    return ''

    @classmethod
    async def wash_html(cls, body):
        '''
        异步清洗html
        :param body:
        :return:
        '''
        body = re.compile('\t|  |\r\n').sub('', body)
        body = re.compile('\n').sub('', body)

        return body

    @classmethod
    async def get_proxy(cls, ip_pool_type=ip_proxy_pool, high_conceal=True,):
        '''
        异步获取proxy
        :return: 格式: 'http://ip:port'
        '''
        # proxy = ip_object._get_random_proxy_ip()    # 失败返回False

        loop = get_event_loop()
        # 设置代理ip
        ip_object = MyIpPools(type=ip_pool_type, high_conceal=high_conceal)
        args = []
        proxy = False
        try:
            proxy = await loop.run_in_executor(None, ip_object._get_random_proxy_ip, *args)
            # print(proxy)
        except Exception:
            pass
        finally:
            try:
                del loop
            except:
                pass
            collect()

            return proxy

    async def run(self):
        url = 'https://superonesfazai.github.io/'

        # 对比发现 总数 越大，aiohttp的效率就比requests更高(100个 aiohttp:35s, requests:43s)
        tasks = [self.loop.create_task(self.aio_get_url_body(url=url, headers=self.headers)) for _ in range(self.max_tasks)]
        finished_job, unfinished_job = await asyncio.wait(tasks)  # tasks是待执行的异步函数的list eg:[hello(), hello(), ...] 进行并行执行
        all_result = [r.result() for r in finished_job]
        # print(all_result)

        return all_result

    def __del__(self):
        self.loop.close()
        gc.collect()

class AioHttp(MyAiohttp):
    '''改名'''
    pass

# if __name__ == '__main__':
#     start_time = time.time()
#     loop = asyncio.get_event_loop()
#     my_aiohttp = MyAiohttp(max_tasks=1)
#     result = loop.run_until_complete(my_aiohttp.run())
#     print(result)
#     end_time = time.time()
#     print('用时: ', end_time - start_time)
#     try: del my_aiohttp
#     except: pass
#     loop.close()
