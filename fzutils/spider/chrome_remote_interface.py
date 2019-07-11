# coding:utf-8

'''
@author = super_fazai
@File    : chrome_remote_interface.py
@connect : superonesfazai@gmail.com
'''

"""
chrome remote interface
"""

from gc import collect
from ..ip_pools import (
    tri_ip_pool,
    get_random_proxy_ip_from_ip_pool,
)
from .fz_driver import (
    PC,
)
from ..common_utils import (
    _print,
    delete_list_null_str,
)
from .pyppeteer_always import *
from ..internet_utils import (
    get_random_pc_ua,
    get_random_phone_ua,
)

__all__ = [
    'ChromiumPuppeteer',
]

# 启动类型
PYPPETEER = 0

PYPPETEER_CHROMIUM_DRIVER_PATH = '/Users/afa/myFiles/tools/pyppeteer_driver/mac/chrome-mac/Chromium.app/Contents/MacOS/Chromium'

class ChromiumPuppeteer(object):
    """
    chromium 操作者
    """
    def __init__(self,
                 type=PYPPETEER,
                 load_images=False,
                 executable_path=PYPPETEER_CHROMIUM_DRIVER_PATH,
                 high_conceal=True,
                 logger=None,
                 headless=False,
                 driver_use_proxy=True,
                 user_agent_type=PC,
                 driver_obj=None,
                 ip_pool_type=tri_ip_pool,
                 driver_cookies=None,
                 driver_auto_close=True,
                 driver_dumpio=False,
                 driver_devtools=False,
                 disable_extensions=True,
                 load_extensions=False,
                 extension_is_switch_proxy=False,
                 extension_path=None,):
        """
        :param type:
        :param load_images:
        :param executable_path:
        :param high_conceal:
        :param logger:
        :param headless: 无头速度不亚于phantomjs
        :param driver_use_proxy:
        :param user_agent_type:
        :param driver_obj:
        :param ip_pool_type:
        :param driver_cookies:
        :param driver_auto_close:
        :param driver_dumpio: 把无头浏览器进程的 stderr 核 stdout pip 到主程序，也就是设置为 True 的话，chromium console 的输出就会在主程序中被打印出来
        :param driver_devtools: 是否打开devtools
        :param disable_extensions: 是否禁用所有扩展
        :param load_extensions: 是否加载扩展程序
        :param extension_is_switch_proxy: 扩展程序是否为修改代理的扩展, ** 使用代理扩展必须进行修改
        :param extension_path: 扩展程序的路径
        """
        super(ChromiumPuppeteer, self).__init__()
        self.type = type
        self.executable_path = executable_path
        self.high_conceal = high_conceal
        self.load_images = load_images
        self.headless = headless
        self.driver_use_proxy = driver_use_proxy
        self.lg = logger
        self.user_agent_type = user_agent_type
        self.ip_pool_type = ip_pool_type
        self._cookies = driver_cookies
        self.driver_auto_close = driver_auto_close
        self.driver_dumpio = driver_dumpio
        self.driver_devtools = driver_devtools
        self.disable_extensions = disable_extensions
        self.load_extensions = load_extensions
        self.extension_is_switch_proxy = extension_is_switch_proxy
        self.extension_path = extension_path
        self.driver = None
        self.driver_obj = driver_obj

    async def create_chromium_puppeteer_browser(self,) -> PyppeteerBrowser:
        """
        创建driver[非阻塞]
        :return:
        """
        _print(msg='init chromium_puppeteer ...', logger=self.lg)
        # 设置代理
        proxy_ip = ''
        if self.driver_use_proxy:
            # 由于在本地提供代理服务所以近乎非阻塞
            proxy_ip = get_random_proxy_ip_from_ip_pool(
                ip_pool_type=self.ip_pool_type,
                high_conceal=self.high_conceal,)
            assert proxy_ip != '', '给chrome设置代理失败, 异常抛出!'
            # print(proxy_ip)

        if self.load_extensions:
            assert self.extension_path is not None, '未设置extension_path'
            # 设置启用所有扩展
            self.disable_extensions = False
            if self.extension_is_switch_proxy:
                # --proxy-server不进行设置, 因为已在修改代理的扩展中进行设置代理
                self.driver_use_proxy = False

        # TODO chrome设置代理进行请求成功率较低
        driver_args = [
            # 禁用扩展
            '--disable-extensions' if self.disable_extensions else '',
            # 隐藏屏幕截图中的滚动条
            '--hide-scrollbars',
            # 禁用Flash的捆绑PPAPI版本
            '--disable-bundled-ppapi-flash',
            # 浏览器静音
            '--mute-audio',
            '--no-sandbox',
            # 取消提示: chrome正在受自动软件控制
            '--disable-infobars',
            # 禁用setuid沙盒(仅限Linux)
            '--disable-setuid-sandbox',
            # 禁用GPU硬件加速
            '--disable-gpu',
            '--proxy-server=http://{0}'.format(proxy_ip) if proxy_ip != '' and self.driver_use_proxy else '',
            '--user-agent={0}'.format(get_random_pc_ua() if self.user_agent_type == PC else get_random_phone_ua()),
            # 修改代理的扩展
            '--load-extension={0}'.format(self.extension_path) if self.load_extensions else '',
        ]
        driver_args = delete_list_null_str(_list=driver_args)
        self.driver = await chromium_launch({
            'headless': self.headless,
            'devtools': self.driver_devtools,
            'executablePath': self.executable_path,
            # 可选args: https://peter.sh/experiments/chromium-command-line-switches/
            'args': driver_args,
            'autoClose': self.driver_auto_close,
            'dumpio': self.driver_dumpio,
        })
        _print(msg='init over!', logger=self.lg)

        return self.driver

    def _get_driver(self):
        '''
        得到driver对象
        :return:
        '''
        return self.driver

    def __del__(self):
        try:
            del self.lg
        except:
            pass
        try:
            self.driver
        except:
            pass
        collect()
