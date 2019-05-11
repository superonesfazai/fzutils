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
from time import sleep

from ..common_utils import _print
from ..spider.async_always import async_sleep
from ..aio_utils import async_wait_tasks_finished

__all__ = [
    # atx
    'u2_block_page_back',                           # [阻塞]u2的页面返回
    'u2_page_back',                                 # u2的页面返回
    'u2_get_device_display_h_and_w',                # u2获取设备的高跟宽
    'u2_get_some_ele_height',                       # u2得到某一个ele块的height
    'u2_block_up_swipe_some_height',                # [阻塞]u2 上滑某个高度
    'u2_up_swipe_some_height',                      # u2上滑某个高度
    'async_get_u2_ele_info',                        # 异步获取u2 ele 的info
    'AndroidDeviceObj',                             # 设备信息类
    'get_u2_init_device_list',                      # 得到初始化u2设备对象list
    'u2_get_device_obj_by_device_id',               # [阻塞]根据device_id初始化获取到device_obj
    'u2_unblock_get_device_obj_by_device_id',       # [异步非阻塞]根据device_id初始化获取到device_obj

    # mitmproxy
    'get_mitm_flow_request_headers_user_agent',     # 获取flow.request.headers的user_agent
]

def u2_block_page_back(d, back_num=1):
    """
    [阻塞]u2的页面返回
    :param d:
    :param back_num:
    :return:
    """
    while back_num > 0:
        d.press('back')
        back_num -= 1
        sleep(.3)

    return

async def u2_page_back(d, back_num=1):
    """
    u2的页面返回
    :param d: eg: u2 d
    :param back_num:
    :return:
    """
    return u2_block_page_back(
        d=d,
        back_num=back_num,)

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

def u2_block_up_swipe_some_height(d, swipe_height, base_height=.1) -> None:
    """
    [阻塞]u2 上滑某个高度
    :param d:
    :param swipe_height:
    :param base_height:
    :return:
    """
    d.swipe(0., base_height + swipe_height, 0., base_height)

async def u2_up_swipe_some_height(d, swipe_height, base_height=.1) -> None:
    """
    u2 上滑某个高度
    :param d:
    :param height:
    :param base_height:
    :return:
    """
    return u2_block_up_swipe_some_height(
        d=d,
        swipe_height=swipe_height,
        base_height=base_height,)

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

class AndroidDeviceObj(object):
    """设备信息类"""
    def __init__(self, d, device_id: str, device_product_name: str):
        """
        init
        :param d: UIAutomatorServer类的对象[from uiautomator2 import UIAutomatorServer]
        :param device_id: 设备唯一id
        :param device_product_name: 设备名称 eg: d.info.get('productName', '')来获得
        """
        self.d = d
        self.device_id = device_id
        self.device_product_name = device_product_name

def u2_get_device_obj_by_device_id(u2,
                                   device_id: str,
                                   pkg_name: str='',
                                   open_someone_pkg=True,
                                   d_debug: bool = False,
                                   set_fast_input_ime=True,
                                   logger=None):
    """
    [阻塞]根据device_id初始化获取到device_obj
    :param u2: import uiautomator2 as u2的u2
    :param device_id:
    :param pkg_name: APP包名
    :param open_someone_pkg: bool 初始化设备时是否打开指定pkg_name
    :param d_debug: 是否为debug模式
    :param set_fast_input_ime:
    :param logger:
    :return:
    """
    _print(msg='init device_id: {} ...'.format(device_id), logger=logger)
    # 设置设备id
    d = u2.connect(addr=device_id)
    d_info = d.info
    _print(msg='{}'.format(d_info), logger=logger)
    device_product_name = d_info.get('productName', '')
    assert device_product_name != '', 'device_product_name !=""'
    d.set_fastinput_ime(set_fast_input_ime)
    d.debug = d_debug

    if open_someone_pkg and pkg_name != '':
        # 启动指定包
        now_session = d.session(pkg_name=pkg_name)

    device_obj = AndroidDeviceObj(
        d=d,
        device_id=device_id,
        device_product_name=device_product_name,)
    _print(msg='init device_id: {} over !'.format(device_id), logger=logger)

    return device_obj

async def u2_unblock_get_device_obj_by_device_id(u2,
                                                 device_id: str,
                                                 pkg_name: str='',
                                                 open_someone_pkg=True,
                                                 d_debug: bool = False,
                                                 set_fast_input_ime=True,
                                                 logger=None):
    """
    [异步非阻塞]根据device_id初始化获取到device_obj
    :param u2: import uiautomator2 as u2的u2
    :param device_id:
    :param pkg_name:
    :param open_someone_pkg: bool 初始化设备时是否打开指定pkg_name
    :param d_debug:
    :param set_fast_input_ime:
    :param logger:
    :return:
    """
    async def _get_args() -> list:
        """获取args"""
        return [
            u2,
            device_id,
            pkg_name,
            open_someone_pkg,
            d_debug,
            set_fast_input_ime,
            logger,
        ]

    loop = get_event_loop()
    args = await _get_args()
    device_obj = None
    try:
        device_obj = await loop.run_in_executor(None, u2_get_device_obj_by_device_id, *args)
    except Exception as e:
        _print(msg='遇到错误:', logger=logger, log_level=2, exception=e)
    finally:
        # loop.close()
        try:
            del loop
        except:
            pass
        collect()

        return device_obj

async def get_u2_init_device_list(loop,
                                  u2,
                                  device_id_list:list,
                                  pkg_name: str = '',
                                  open_someone_pkg=True,
                                  d_debug=False,
                                  set_fast_input_ime=True,
                                  logger=None) -> list:
    """
    得到初始化u2设备对象list
    :param loop:
    :param u2: import uiautomator2 as u2的u2
    :param device_id_list: eg: ['816QECTK24ND8', ...]
    :param pkg_name: app 包名
    :param open_someone_pkg: bool 初始化设备时是否打开指定pkg_name
    :param d_debug: u2 是否为调试模式
    :param set_fast_input_ime:
    :param logger:
    :return:
    """
    device_obj_list = []
    tasks = []
    for device_id in device_id_list:
        tasks.append(loop.create_task(u2_unblock_get_device_obj_by_device_id(
            u2=u2,
            device_id=device_id,
            pkg_name=pkg_name,
            open_someone_pkg=open_someone_pkg,
            d_debug=d_debug,
            set_fast_input_ime=set_fast_input_ime,
            logger=logger,)))

    all_res = await async_wait_tasks_finished(tasks=tasks)
    # pprint(all_res)
    for device_obj in all_res:
        device_obj_list.append(device_obj)

    try:
        del tasks
    except:
        pass

    return device_obj_list