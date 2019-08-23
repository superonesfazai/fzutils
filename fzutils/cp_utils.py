# coding:utf-8

# cp的utils

import json
import asyncio
import re
import execjs
import time
import requests
from gc import collect
from random import randint
from decimal import Decimal
from asyncio import (
    get_event_loop,
    new_event_loop,)

from .common_utils import _print
from .time_utils import (
    string_to_datetime,
    get_shanghai_time,)
from .safe_utils import get_uuid3
from .safe_utils import md5_encrypt
from .ip_pools import (
    IpPools,
    fz_ip_pool,
    ip_proxy_pool,)

__all__ = [
    'get_shelf_time_and_delete_time',                       # cp得到shelf_time和delete_time
    'get_miaosha_begin_time_and_miaosha_end_time',          # cp返回秒杀开始和结束时间
    'filter_invalid_comment_content',                       # cp过滤无效comment

    # tb签名相关
    'block_calculate_tb_right_sign',                        # 阻塞方式计算tb sign
    'block_get_tb_sign_and_body',                           # 阻塞方式获取淘宝加密sign接口数据
    'calculate_right_sign',                                 # 获取淘宝sign
    'get_taobao_sign_and_body',                             # 得到淘宝带签名sign的接口数据
    'unblock_get_taobao_sign_and_body',                     # 非阻塞获取tb sign body
]

def get_shelf_time_and_delete_time(tmp_data, is_delete, shelf_time, delete_time):
    '''
    公司得到my_shelf_and_down_time和delete_time
    :param tmp_data:
    :param is_delete:
    :param shelf_time: datetime or ''
    :param delete_time: datetime or ''
    :return: delete_time datetime or '', shelf_time datetime or ''
    '''
    tmp_shelf_time = shelf_time if shelf_time is not None else ''
    tmp_down_time = delete_time if delete_time is not None else ''
    _ = str(get_shanghai_time())
    # print('最新状态: {}, 原先状态: {}'.format(tmp_data['is_delete'], is_delete))

    # 设置最后刷新的商品状态上下架时间
    # 1. is_delete由0->1 为下架时间点 delete_time
    # 2. is_delete由1->0 为上架时间点 shelf_time
    if tmp_data['is_delete'] != is_delete:
        # 表示状态改变
        # print('商品状态改变!')
        if is_delete == 1 and tmp_data['is_delete'] == 0:
            # is_delete由1->0 表示商品状态下架变为上架，记录上架时间点
            shelf_time = _
            delete_time = tmp_down_time
        else:
            # is_delete由0->1 表示商品状态上架变为下架，记录下架时间点
            shelf_time = tmp_shelf_time
            delete_time = _

    else:
        # 表示状态不变
        # print('商品状态不变!')
        if tmp_data['is_delete'] == 0:
            # 原先还是上架状态的
            if tmp_shelf_time == '':
                if tmp_down_time == '':
                    shelf_time = _
                    delete_time = ''
                else:
                   shelf_time = _
                   delete_time = tmp_down_time
            else:
                if tmp_down_time == '':
                    shelf_time = tmp_shelf_time
                    delete_time = ''
                else:
                    shelf_time = tmp_shelf_time
                    delete_time = tmp_down_time
                    if delete_time > shelf_time:
                        shelf_time = _
                    else:
                        pass

        else:
            # 原先还是下架状态的
            if tmp_shelf_time == '':
                if tmp_down_time == '':
                    shelf_time = ''
                    delete_time = _
                else:
                    shelf_time = ''
                    delete_time = tmp_down_time
            else:
                if tmp_down_time == '':
                    shelf_time = tmp_shelf_time
                    delete_time = _
                else:
                    shelf_time = tmp_shelf_time
                    delete_time = tmp_down_time
                    # 处理原先下架的商品, 上架时间点>下架时间点
                    if shelf_time > delete_time:
                        # print('上架时间点大于下架时间点')
                        # 修改上架时间小于下架时间
                        delete_time = _
                    else:
                        pass

    # print('shelf_time: {}, delete_time: {}'.format(shelf_time, delete_time))

    return (shelf_time, delete_time)

def block_calculate_tb_right_sign(_m_h5_tk: str, data: json) -> tuple:
    """
    阻塞方式计算tb sign
    :param _m_h5_tk:
    :param data:
    :return: sign 类型str, t 类型str
    """
    # with open('../static/js/get_h_func.js', 'r') as f:  # 打开js源文件
    #     js = f.read()
    #
    # 编译js得到python解析对象
    # js_parser = execjs.compile(js)
    # time.time().__round__() 表示保留到个位
    t = str(time.time().__round__()) + str(randint(100, 999))

    # 构造参数e
    appKey = '12574478'
    # e = 'undefine' + '&' + t + '&' + appKey + '&' + '{"optStr":"{\"displayCount\":4,\"topItemIds\":[]}","bizCode":"tejia_003","currentPage":"1","pageSize":"4"}'
    e = _m_h5_tk + '&' + t + '&' + appKey + '&' + data

    # sign = js_parser.call('h', e)
    sign = md5_encrypt(e)

    return sign, t

def block_get_tb_sign_and_body(base_url,
                               headers:dict,
                               params:dict,
                               data:json,
                               cookies=None,
                               timeout=13,
                               _m_h5_tk='undefine',
                               session=None,
                               logger=None,
                               encoding='utf-8',
                               ip_pool_type=ip_proxy_pool) -> tuple:
    """
    阻塞方式获取淘宝加密sign接口数据
    :return:
    """
    sign, t = block_calculate_tb_right_sign(data=data, _m_h5_tk=_m_h5_tk)
    # print(sign, t)
    headers['Host'] = re.compile(r'://(.*?)/').findall(base_url)[0]
    params.update({  # 添加下面几个query string
        't': t,
        'sign': sign,
        'data': data,
    })

    ip_object = IpPools(type=ip_pool_type)
    tmp_proxies = {
        'http': ip_object._get_random_proxy_ip(),  # 失败返回False
    }
    session = requests.session() if session is None else session
    try:
        response = session.get(
            url=base_url,
            headers=headers,
            params=params,
            cookies=cookies,
            proxies=tmp_proxies,
            timeout=timeout,)
        _m_h5_tk = response.cookies.get('_m_h5_tk', '').split('_')[0]
        # logger.info(str(s.cookies.items()))
        # logger.info(str(_m_h5_tk))
        # print(str(response.cookies.items()))
        # print(_m_h5_tk)

        body = response.content.decode(encoding)
        # logger.info(str(body))

    except Exception:
        logger.error('遇到错误:', exc_info=True)
        _m_h5_tk = ''
        body = ''

    return (_m_h5_tk, session, body)

async def calculate_right_sign(_m_h5_tk: str, data: json) -> tuple:
    '''
    根据给的json对象 data 和 _m_h5_tk计算出正确的sign
    :param _m_h5_tk:
    :param data:
    :return: sign 类型str, t 类型str
    '''
    return block_calculate_tb_right_sign(
        _m_h5_tk=_m_h5_tk,
        data=data)

async def get_taobao_sign_and_body(*params, **kwargs) -> tuple:
    '''
    得到淘宝加密签名sign接口数据
    :param base_url:
    :param headers:
    :param params:
    :param data:
    :param timeout:
    :param _m_h5_tk:
    :param session:
    :return: (_m_h5_tk, session, body)
    '''
    return block_get_tb_sign_and_body(*params, **kwargs)

def get_miaosha_begin_time_and_miaosha_end_time(miaosha_time):
    '''
    返回秒杀开始和结束时间
    :param miaosha_time: 里面的miaosha_begin_time的类型为字符串类型
    :return: tuple  miaosha_begin_time, miaosha_end_time
    '''
    miaosha_begin_time = miaosha_time.get('miaosha_begin_time')
    miaosha_end_time = miaosha_time.get('miaosha_end_time')

    if miaosha_begin_time is None or miaosha_end_time is None:
        miaosha_begin_time = miaosha_time.get('begin_time')
        miaosha_end_time = miaosha_time.get('end_time')

    # 将字符串转换为datetime类型
    miaosha_begin_time = string_to_datetime(miaosha_begin_time)
    miaosha_end_time = string_to_datetime(miaosha_end_time)

    return miaosha_begin_time, miaosha_end_time

def filter_invalid_comment_content(_comment_content) -> bool:
    '''
    过滤无效评论
    :param _comment_content:
    :return:
    '''
    filter_str = '''
    此用户没有填写|评价方未及时做出评价|系统默认好评!|
    假的|坏的|差的|差评|退货|不想要|无良商家|再也不买|
    我也是服了|垃圾|打电话骂人|骚扰|狗屁东西|sb|SB
    MB|mb|质量太差|破|粗糙|不好用|不怎么好用
    '''.replace(' ', '').replace('\n', '')
    if re.compile(filter_str).findall(_comment_content) != []\
            or _comment_content.__len__() <= 3:
        return False
    else:
        return True

async def unblock_get_taobao_sign_and_body(base_url,
                                           headers: dict,
                                           params: dict,
                                           data: json,
                                           timeout=13,
                                           _m_h5_tk='undefine',
                                           session=None,
                                           logger=None,
                                           encoding='utf-8',
                                           ip_pool_type=ip_proxy_pool) -> tuple:
    """
    非阻塞获取tb sign body
    :param base_url:
    :param headers:
    :param params:
    :param data:
    :param timeout:
    :param _m_h5_tk:
    :param session:
    :param logger:
    :param encoding:
    :param ip_pool_type:
    :return:
    """
    def _get_taobao_sign_and_body(*args, **kwargs):
        new_loop = new_event_loop()
        res = new_loop.run_until_complete(get_taobao_sign_and_body(*args, **kwargs))
        try:
            del new_loop
        except:
            pass
        # print(res)

        return res

    async def _get_args() -> list:
        return [
            base_url,
            headers,
            params,
            data,
            timeout,
            _m_h5_tk,
            session,
            logger,
            encoding,
            ip_pool_type,
        ]

    loop = get_event_loop()
    args = await _get_args()
    try:
        res = await loop.run_in_executor(None, _get_taobao_sign_and_body, *args)
        # print(res)
    except Exception as e:
        _print(msg='遇到错误:', logger=logger, log_level=2, exception=e)
    finally:
        loop.close()
        try:
            del loop
        except:
            pass
        collect()

        return res
