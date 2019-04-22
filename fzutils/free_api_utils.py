# coding:utf-8

'''
@author = super_fazai
@File    : free_api_utils.py
@connect : superonesfazai@gmail.com
'''

"""
一些免费api 接口的封装
"""

from pprint import pprint
import re

from .ip_pools import tri_ip_pool
from .spider.fz_requests import Requests
from .common_utils import json_2_dict
from .internet_utils import get_random_pc_ua

__all__ = [
    'get_jd_one_goods_price_info',                              # 获取京东单个商品价格
    'get_express_info',                                         # 获取快递信息
    'get_phone_num_info',                                       # 获取手机号信息
    'get_baidu_baike_info',                                     # 获取某关键字的百度百科信息
    'get_bd_map_shop_info_list_by_keyword_and_area_name',       # 根据关键字和区域检索店铺信息(百度api 关键字搜索服务)[测试最多前400个]
]

def get_jd_one_goods_price_info(goods_id) -> list:
    '''
    获取京东单个商品价格
    :param goods_id: 商品id
    :return:
    '''
    base_url = 'http://p.3.cn/prices/mgets'
    params = (
        ('skuIds', 'J_' + goods_id),
    )
    body = Requests.get_url_body(url=base_url, use_proxy=False, params=params)

    return json_2_dict(body, default_res=[])

def get_express_info(express_type, express_id) -> dict:
    '''
    获取快递信息
    express_type: ps: 传字典对应的value
        {
            '申通': 'shentong',
            'ems': 'ems',
            '顺丰': 'shunfeng',
            '圆通': 'yuantong',
            '中通': 'zhongtong',
            '韵达': 'yunda',
            '天天': 'tiantian',
            '汇通': 'huitongkuaidi',
            '全峰': 'quanfengkuaidi',
            '德邦': 'debangwuliu',
            '宅急送': 'zhaijisong',
            ...
        }
    :param express_type: 快递公司名
    :param express_id: 快递号
    :return:
    '''
    base_url = 'http://www.kuaidi100.com/query'
    params = (
        ('type', express_type),
        ('postid', express_id),
    )
    body = Requests.get_url_body(url=base_url, use_proxy=False, params=params)

    return json_2_dict(body)

def get_phone_num_info(phone_num) -> dict:
    '''
    获取手机号信息
    :param phone_num: 手机号
    :return:
    '''
    url = 'https://tcc.taobao.com/cc/json/mobile_tel_segment.htm'
    params = (
        ('tel', str(phone_num)),
    )

    body = Requests.get_url_body(url=url, params=params, use_proxy=False)
    try:
        res = re.compile('__GetZoneResult_ = (.*)').findall(body)[0]
        return json_2_dict(res)
    except IndexError:
        return {}

def get_baidu_baike_info(keyword, bk_length=1000) -> dict:
    '''
    获取某关键字的百度百科信息
    :param keyword:
    :return:
    '''
    url = 'http://baike.baidu.com/api/openapi/BaikeLemmaCardApi'
    params = (
        ('scope', '103'),
        ('format', 'json'),
        ('appid', '379020'),
        ('bk_key', str(keyword)),
        ('bk_length', str(bk_length)),
    )
    body = Requests.get_url_body(
        url=url,
        params=params,
        use_proxy=False)

    return json_2_dict(body)

def get_bd_map_shop_info_list_by_keyword_and_area_name(ak:str,
                                                       keyword:str,
                                                       area_name:str,
                                                       page_num:int,
                                                       page_size:int=20,
                                                       use_proxy=True,
                                                       ip_pool_type=tri_ip_pool,
                                                       num_retries=6,
                                                       timeout=20,) -> list:
    """
    根据关键字和区域检索店铺信息(百度api 关键字搜索服务)[测试最多前400个]
    :param ak: 百度地图申请的ak
    :param keyword: eg: '鞋子'
    :param area_name: eg: '杭州' 待搜索的区域, 多为省份, 城市, 具体区域
    :param page_num: start 1
    :param page_size: 固定
    :param ip_pool_type:
    :param num_retries:
    :return:
    """
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': get_random_pc_ua(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    params = (
        ('query', str(keyword)),
        ('region', str(area_name)),
        ('output', 'json'),
        ('ak', str(ak)),
        ('page_num', str(page_num)),
        ('page_size', str(page_size)),
    )
    url = 'http://api.map.baidu.com/place/v2/search'
    body = Requests.get_url_body(
        url=url,
        headers=headers,
        params=params,
        use_proxy=use_proxy,
        ip_pool_type=ip_pool_type,
        num_retries=num_retries,
        timeout=timeout,)
    # print(body)
    data = json_2_dict(
        json_str=body,
        default_res={}, ).get('results', [])
    # pprint(data)

    return data