# coding:utf-8

'''
@author = super_fazai
@File    : app_utils.py
@connect : superonesfazai@gmail.com
'''

"""
app utils
"""

from ..spider.async_always import async_sleep

__all__ = [
    # atx
    'u2_page_back',                     # u2的页面返回
    'u2_get_device_display_h_and_w',    # u2获取设备的高跟宽
    'u2_get_some_ele_height',           # u2得到某一个ele块的height
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