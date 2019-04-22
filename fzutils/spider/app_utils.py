# coding:utf-8

'''
@author = super_fazai
@File    : app_utils.py
@connect : superonesfazai@gmail.com
'''

"""
app utils
"""

from gc import collect
from asyncio import get_event_loop
from pprint import pprint

from ..common_utils import _print
from ..spider.async_always import async_sleep

__all__ = [
    # atx
    'u2_page_back',                                 # u2的页面返回
    'u2_get_device_display_h_and_w',                # u2获取设备的高跟宽
    'u2_get_some_ele_height',                       # u2得到某一个ele块的height
    'u2_up_swipe_some_height',                      # u2上滑某个高度
    'async_get_u2_ele_info',                        # 异步获取u2 ele 的info

    # mitmproxy
    'get_mitm_flow_request_headers_user_agent',     # 获取flow.request.headers的user_agent
]

async def u2_page_back(d, back_num=1):
    """
    u2的页面返回
    :param d: eg: u2 d
    :param back_num:
    :return:
    """
    while back_num > 0:
        d.press('back')
        back_num -= 1
        await async_sleep(.3)

    return

async def u2_get_device_display_h_and_w(d) -> tuple:
    """
    u2获取设备的高跟宽
    :param d: eg: u2 d
    :return:
    """
    device_height = d.device_info.get('display', {}).get('height')
    device_width = d.device_info.get('display', {}).get('width')

    return device_height, device_width

async def u2_get_some_ele_height(ele):
    """
    u2得到某一个ele块的height
    :param ele: eg: d(resourceId="com.taobao.taobao:id/topLayout")
    :return:
    """
    return ele.info.get('bounds', {}).get('bottom') \
           - ele.info.get('bounds', {}).get('top')

async def u2_up_swipe_some_height(d, swipe_height, base_height=.1) -> None:
    """
    u2 上滑某个高度
    :param d:
    :param height:
    :param base_height:
    :return:
    """
    d.swipe(0., base_height + swipe_height, 0., base_height)

async def async_get_u2_ele_info(ele, logger=None) -> tuple:
    """
    异步获取ele 的info
    :param ele: UiObject [from uiautomator2.session import UiObject]
    :return: (ele, ele_info)
    """
    async def _get_args() -> list:
        '''获取args'''
        return [
            ele,
        ]

    def _get_ele_info(ele) -> dict:
        return ele.info

    loop = get_event_loop()
    args = await _get_args()
    ele_info = {}
    try:
        ele_info = await loop.run_in_executor(None, _get_ele_info, *args)
        # print('*' * 50)
        # print(ele_info)
    except Exception as e:
        _print(msg='遇到错误:', logger=logger, log_level=2, exception=e)
    finally:
        # loop.close()
        try:
            del loop
        except:
            pass
        _print(
            msg='[{}] ele: {}'.format('+' if ele_info != {} else '-', ele),
            logger=logger,)
        collect()

        return ele, ele_info

def get_mitm_flow_request_headers_user_agent(headers, logger=None) -> str:
    """
    获取flow.request.headers的user_agent
    :param headers: flow.request.headers obj
    :return:
    """
    user_agent = ''
    try:
        headers = dict(headers)
        # pprint(headers)
        for key, value in headers.items():
            if key == 'user-agent':
                user_agent = value
                break
            else:
                continue
        assert user_agent != '', 'user_agent不为空str!'
    except Exception as e:
        _print(
            msg='遇到错误',
            logger=logger,
            exception=e,
            log_level=2)

    return user_agent