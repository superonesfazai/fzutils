# coding:utf-8

'''
@author = super_fazai
@File    : my_phantomjs.py
@Time    : 2017/3/21 15:30
@connect : superonesfazai@gmail.com
'''
import sys
sys.path.append('..')

from ..ip_pools import (
    MyIpPools,
    ip_proxy_pool,
    fz_ip_pool,
    tri_ip_pool,)
from ..internet_utils import (
    get_random_pc_ua,
    get_random_phone_ua,
    driver_cookies_list_2_str,)
from ..common_utils import _print

# from fzutils.ip_pools import (
#     MyIpPools,
#     ip_proxy_pool,
#     fz_ip_pool,
#     tri_ip_pool,)
# from fzutils.internet_utils import (
#     get_random_pc_ua,
#     get_random_phone_ua,
#     driver_cookies_list_2_str,)
# from fzutils.common_utils import _print

from selenium import webdriver
# WebDriver
from selenium.webdriver.remote.webdriver import WebDriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    WebDriverException,
    NoSuchElementException,
)
from scrapy.selector import Selector

import re
from gc import collect
from time import sleep
import os
import shutil
from zipfile import ZipFile

__all__ = [
    'MyPhantomjs',
    'BaseDriver',
    'ChromeExtensioner',
]

PHANTOMJS_DRIVER_PATH = '/Users/afa/myFiles/tools/phantomjs-2.1.1-macosx/bin/phantomjs'
CHROME_DRIVER_PATH = '/Users/afa/myFiles/tools/chromedriver'
FIREFOX_DRIVER_PATH = '/Users/afa/myFiles/tools/geckodriver'

# phantomjs驱动地址
EXECUTABLE_PATH = PHANTOMJS_DRIVER_PATH

# 启动类型
CHROME = 0
PHANTOMJS = 1
FIREFOX = 2

# user-agent类型
PC = 0
PHONE = 1

class MyPhantomjs(object):
    def __init__(self,
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
                 driver_cookies=None,):
        '''
        初始化
        :param load_images: 是否加载图片
        :param high_conceal: ip是否高匿
        :param headless: 是否为无头浏览器(针对chrome, firefox)
        :param driver_use_proxy: chrome是否使用代理
        :param user_agent_type: user-agent类型
        :param driver_obj: webdriver对象
        :param ip_pool_type: ip_pool type
        :param extension_path: 扩展插件路径
        '''
        super(MyPhantomjs, self).__init__()
        self.type = type
        self.high_conceal = high_conceal
        self.executable_path = executable_path
        self.load_images = load_images
        self.headless = headless
        self.driver_use_proxy = driver_use_proxy
        self.lg = logger
        self.user_agent_type = user_agent_type
        self.ip_pool_type = ip_pool_type
        self.extension_path = extension_path
        self._cookies = driver_cookies
        if driver_obj is None:
            self._set_driver()
        else:
            self.driver = driver_obj

    def _set_driver(self, num_retries=4):
        '''
        初始化self.driver，并且出错重试
        :param num_retries: 重试次数
        :return:
        '''
        try:
            if self.type == PHANTOMJS:
                self._init_phantomjs()
            elif self.type == CHROME:
                self._init_chrome()
            elif self.type == FIREFOX:
                self._init_firefox()
            else:
                raise ValueError('type赋值异常!请检查!')
        except Exception as e:
            # _print(msg='初始化phantomjs时出错:', logger=self.lg, log_level=2, exception=e)
            if num_retries > 0:
                return self._set_driver(num_retries=num_retries-1)
            else:
                _print(msg='初始化phantomjs时出错:', logger=self.lg, log_level=2, exception=e)
                raise e

    def _init_phantomjs(self):
        """
        初始化带cookie的驱动，之所以用phantomjs是因为其加载速度很快(快过chrome驱动太多)
        """
        _print(msg='init phantomjs ...', logger=self.lg)
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap['phantomjs.page.settings.resourceTimeout'] = 1000  # 1秒
        cap['phantomjs.page.settings.loadImages'] = self.load_images
        cap['phantomjs.page.settings.disk-cache'] = True
        cap['phantomjs.page.settings.userAgent'] = get_random_pc_ua() if self.user_agent_type == PC else get_random_phone_ua()
        if self._cookies is not None:
            if self._cookies != '':
                cap['phantomjs.page.customHeaders.Cookie'] = self._cookies

        self.driver = webdriver.PhantomJS(executable_path=self.executable_path, desired_capabilities=cap)

        wait = ui.WebDriverWait(self.driver, 20)  # 显示等待n秒, 每过0.5检查一次页面是否加载完毕
        _print(msg='init over!', logger=self.lg)

        return True

    def _init_chrome(self):
        '''
        如果使用chrome请设置page_timeout=30(可用)
        :return:
        '''
        _print(msg='init chrome...', logger=self.lg)
        chrome_options = webdriver.ChromeOptions()
        # 设置headless
        if self.headless:
            chrome_options.add_argument('--headless')     # 注意: 设置headless无法访问网页

        chrome_options.add_argument('--disable-gpu')    # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--no-sandbox')  # required when running as root user. otherwise you would get no sandbox errors.
        # chrome_options.add_argument('window-size=1200x600')   # 设置窗口大小

        # 设置无图模式
        chrome_options.add_argument('blink-settings=imagesEnabled={0}'.format('true' if self.load_images else 'false'))

        '''无法打开https解决方案'''
        # 配置忽略ssl错误
        capabilities = webdriver.DesiredCapabilities.CHROME.copy()
        capabilities['acceptSslCerts'] = True
        capabilities['acceptInsecureCerts'] = True

        # 设置插件
        if self.extension_path is not None:
            chrome_options.add_argument(self.extension_path)

        # 设置代理
        if self.driver_use_proxy:
            proxy_ip = self._get_random_proxy_ip()
            assert proxy_ip != '', '给chrome设置代理失败, 异常抛出!'
            chrome_options.add_argument('--proxy-server=http://{0}'.format(proxy_ip))

        # 修改user-agent
        chrome_options.add_argument('--user-agent={0}'.format(get_random_pc_ua() if self.user_agent_type == PC else get_random_phone_ua()))

        chrome_options.add_experimental_option('excludeSwitches', ['ignore-certificate-errors'])    # 忽视证书错误
        chrome_options.add_argument('--allow-running-insecure-content')

        self.driver = webdriver.Chrome(
            executable_path=self.executable_path,
            chrome_options=chrome_options,
            desired_capabilities=capabilities
        )
        wait = ui.WebDriverWait(self.driver, 30)  # 显示等待n秒, 每过0.5检查一次页面是否加载完毕
        _print(msg='init over!', logger=self.lg)

        return True

    def _init_firefox(self):
        '''
        firefox初始化
        :return:
        '''
        _print(msg='init firefox...', logger=self.lg)
        options = webdriver.FirefoxOptions()
        profile = webdriver.FirefoxProfile()

        # 设置headless
        if self.headless:
            options.add_argument('--headless')

        # 设置无图模式
        if not self.load_images:
            profile.set_preference('permissions.default.stylesheet', 2)
            profile.set_preference('permissions.default.image', 2)
            profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

        # 设置扩展插件
        if self.extension_path is not None:
            profile.add_extension(extension=self.extension_path)                   # 加载插件
            profile.set_preference('extensions.firebug.allPagesActivation', 'on')   # 激活插件

        # 设置代理
        if self.driver_use_proxy:                                                   # 可以firefox通过about:config查看是否正确设置
            proxy_ip = self._get_random_proxy_ip()
            assert proxy_ip != '', '给chrome设置代理失败, 异常抛出!'
            ip = proxy_ip.split(':')[0]
            port = proxy_ip.split(':')[1]
            profile.set_preference("network.proxy.type", 1)                         # 默认是0, 1表示手工配置
            profile.set_preference("network.proxy.http", ip)
            profile.set_preference("network.proxy.http_port", port)
            profile.set_preference('network.proxy.ssl', ip)
            profile.set_preference('network.proxy.ssl_port', port)
            profile.set_preference('network.proxy.socks', ip)
            profile.set_preference('network.proxy.socks_port', port)
            profile.set_preference('network.proxy.ftp', ip)
            profile.set_preference('network.proxy.ftp_port', port)

        # 设置user-agent
        profile.set_preference("general.useragent.override", get_random_pc_ua() if self.user_agent_type == PC else get_random_phone_ua())

        self.driver = webdriver.Firefox(
            executable_path=self.executable_path,
            firefox_options=options,
            firefox_profile=profile
        )
        ui.WebDriverWait(self.driver, 30)  # 显示等待n秒, 每过0.5检查一次页面是否加载完毕
        _print(msg='init over!', logger=self.lg)

        return True

    def from_ip_pool_set_proxy_ip_to_phantomjs(self) -> bool:
        '''
        给phantomjs切换代理
        :return:
        '''
        proxy_ip = self._get_random_proxy_ip()
        assert proxy_ip != '', '动态切换ip失败!'

        try:
            tmp_js = {
                'script': 'phantom.setProxy({}, {});'.format(proxy_ip.split(':')[0], proxy_ip.split(':')[1]),   # 切割成['xxxx', '端口']
                'args': []
            }
            self.driver.command_executor._commands['executePhantomScript'] = ('POST', '/session/$sessionId/phantom/execute')
            self.driver.execute('executePhantomScript', tmp_js)
        except Exception:
            raise AssertionError('动态切换ip失败!')

        return True

    def use_phantomjs_to_get_url_body(self, url, css_selector='', exec_code='', timeout=20):
        '''
        通过phantomjs来获取url的body
        :param url: 待获取的url
        :return: 字符串类型
        '''
        if self.type == PHANTOMJS:
            try:
                self.from_ip_pool_set_proxy_ip_to_phantomjs()
            except Exception:
                try:    # 第二次尝试
                    self.from_ip_pool_set_proxy_ip_to_phantomjs()
                except Exception:
                    _print(msg='动态切换ip失败!', logger=self.lg, log_level=2)
                    return ''
        else:                                                               # 其他类型不动态改变代理
            pass

        try:
            self.driver.set_page_load_timeout(timeout)
        except:
            try: self.driver.set_page_load_timeout(timeout)
            except:
                return ''

        try:
            self.driver.get(url)
            self.driver.implicitly_wait(timeout)                            # 隐式等待和显式等待可以同时使用

            if css_selector != '':
                locator = (By.CSS_SELECTOR, css_selector)
                try:
                    WebDriverWait(self.driver, timeout, 0.5).until(EC.presence_of_element_located(locator))
                except Exception as e:
                    _print(msg='遇到错误: ', logger=self.lg, log_level=2, exception=e)
                    return ''
                else:
                    _print(msg='{0}加载完毕'.format(css_selector), logger=self.lg)

            # self.driver.save_screenshot('tmp_screen.png')
            if exec_code != '':                                             # 动态执行代码
                try:                                                        # 执行代码前先替换掉'  '
                    _ = compile(exec_code.replace('  ', ''), '', 'exec')
                    exec(_)
                except Exception as e:
                    # self.driver.save_screenshot('tmp_screen.png')
                    # _print(exception=e, logger=self.lg)
                    _print(msg='动态执行代码时出错!', logger=self.lg, log_level=2)
                    return ''
                # self.driver.save_screenshot('tmp_screen.png')

            main_body = self._wash_html(self.driver.page_source)
            # _print(msg=str(main_body), logger=self.lg)
        except Exception as e:                                              # 如果超时, 终止加载并继续后续操作
            _print(msg='-->>time out after {0} seconds when loading page'.format(timeout), logger=self.lg, log_level=2)
            _print(msg='报错如下: ', logger=self.lg, log_level=2, exception=e)
            try:
                self.driver.execute_script('window.stop()')                 # 终止后续js执行
            except Exception: pass                                          # 内部urllib.error.URLError or WebDriverException
            _print(msg='main_body为空!', logger=self.lg, log_level=2)
            main_body = ''

        return main_body

    def get_url_body(self, url, css_selector='', exec_code='', timeout=20):
        '''
        重命名
        :param url:
        :param css_selector:
        :param exec_code:
        :param timeout:
        :return:
        '''
        return self.use_phantomjs_to_get_url_body(
            url=url,
            css_selector=css_selector,
            exec_code=exec_code,
            timeout=timeout)

    def get_url_cookies_from_phantomjs_session(self, url, css_selector='', exec_code='', timeout=20):
        '''
        从session中获取cookies
        :param url:
        :return: cookies 类型 str
        '''
        _print(msg='正在获取cookies...请耐心等待...', logger=self.lg)
        self.use_phantomjs_to_get_url_body(
            url=url,
            css_selector=css_selector,
            exec_code=exec_code,
            timeout=timeout)
        cookies_str = ''
        try:
            cookies_list = self.driver.get_cookies()
            cookies_str = driver_cookies_list_2_str(cookies_list=cookies_list)
            # _print(msg=str(cookies), logger=self.lg)
        except Exception as e:
            _print(msg='遇到错误:', logger=self.lg, exception=e, log_level=2)

        return cookies_str

    def _get_random_proxy_ip(self) -> str:
        '''
        得到一个随机代理
        :return: 格式: ip:port or ''
        '''
        ip_object = MyIpPools(type=self.ip_pool_type, high_conceal=self.high_conceal)
        _ = ip_object._get_random_proxy_ip()
        proxy_ip = re.compile(r'https://|http://').sub('', _) if isinstance(_, str) else ''

        return proxy_ip

    def _wash_html(self, html):
        '''
        清洗html
        :param html:
        :return:
        '''
        html = re.compile('\n|\t|  ').sub('', html)

        return html

    def _get_cookies(self) -> dict:
        '''
        得到当前页面的cookies
        :return:
        '''
        cookies_list = self.driver.get_cookies()
        res = {}
        [res.update({i.get('name', ''): i.get('value', '')}) for i in cookies_list]

        return res

    def _get_driver(self):
        '''
        得到driver对象
        :return:
        '''
        return self.driver

    def find_element(self, by=By.CSS_SELECTOR, value=None):
        """
        查找单个element
        :param by:
        :param value:
        :return:
        """
        return self.driver.find_element(by=by, value=value)

    def find_elements(self, by=By.CSS_SELECTOR, value=None):
        """
        查找elements
        :param by:
        :param value:
        :return:
        """
        return self.driver.find_elements(by=by, value=value)

    def save_screenshot(self, file_name):
        """
        屏幕截图
        :param file_name: 保存的路径 eg: '/Screenshots/foo.png'
        :return:
        """
        return self.driver.save_screenshot(filename=file_name)

    def add_cookie(self, cookies_dict):
        """
        添加某个cookie 2 driver
        :param cookies_dict: eg: {'name' : 'foo', 'value' : 'bar'}
        :return:
        """
        self.driver.add_cookie(cookies_dict=cookies_dict)

    def delete_cookie(self, name):
        """
        删除某个cookie
        :param name:
        :return:
        """
        self.driver.delete_cookie(name=name)

    def delete_all_cookies(self):
        """
        删除driver所有cookies
        :return:
        """
        self.driver.delete_all_cookies()

    def execute_script(self, script, *args):
        """
        执行js
        :param script:
        :param args:
        :return:
        """
        return self.driver.execute_script(script=script, *args)

    def execute_async_script(self, script, *args):
        """
        执行异步js
        :param script:
        :param args:
        :return:
        """
        return self.driver.execute_async_script(script=script, *args)

    def close_current_window(self):
        """
        关闭当前窗口
        :return:
        """
        self.driver.close()

    def back(self):
        """
        当前页面回退
        :return:
        """
        self.driver.back()

    def refresh(self):
        """
        当前页面刷新
        :return:
        """
        self.driver.refresh()

    def forward(self):
        """
        返回前一页
        :return:
        """
        self.driver.forward()

    @property
    def switch_to(self):
        return self.driver.switch_to

    def switch_to_window(self, window_name):
        """
        切换到某个tab window(切换到某个窗口句柄)
        :param window_name:
        :return:
        """
        self.driver.switch_to_window(window_name=window_name)

    def switch_to_active_element(self):
        """
        切换到当前的活跃元素
        :return:
        """
        return self.driver.switch_to_active_element()

    def switch_to_alert(self):
        """
        切换到alert弹窗
        :return: 一个alert对象, 后续eg: alert = driver.switch_to_alert() alert.send_keys()
        """
        return self.driver.switch_to_alert()

    def switch_to_default_content(self):
        """
        切换回默认内容
        :return:
        """
        return self.driver.switch_to_default_content()

    def switch_to_frame(self, frame_reference):
        """
        Deprecated use driver.switch_to.frame
        """
        return self.driver.switch_to_frame(frame_reference=frame_reference)

    @property
    def current_url(self):
        """
        获取当前的url
        :return:
        """
        return self.driver.current_url

    @property
    def page_source(self):
        """
        当前页面的html
        :return:
        """
        return self.driver.page_source

    @property
    def current_window_handle(self) -> str:
        """
        获取当前窗口句柄name
        :return:
        """
        return self.driver.current_window_handle

    @property
    def window_handles(self) -> list:
        """
        获取所有窗口句柄name list
        :return:
        """
        return self.driver.window_handles

    def __del__(self):
        try:
            self.driver.quit()
            del self.lg
        except:
            pass
        collect()

class BaseDriver(MyPhantomjs):
    '''改名'''
    pass

class ChromeExtensioner(object):
    '''
    chrome扩展插件: 旨在动态设置代理
        用法:
            chrome_options = webdriver.ChromeOptions()
            ext = ChromeExtensioner()
            chrome_options.add_argument('--load-extension={0}'.format(ext.get_extension_dir_path()))
    '''
    def __init__(self, extension_dir='./extensions', schema='http',
                 host='127.0.0.1', port='8000', username='', passwd=''):
        self.extension_dir = extension_dir
        self.ip_pools_info = {
            'schema': schema,
            'host': host,
            'port': port,
            'username': username,
            'password': passwd,
        }

    def get_extension_dir_path(self):
        '''
        本地先生成插件内容, 再返回插件路径
        :return:
        '''
        path = "{0}/{1}_{2}".format(self.extension_dir, self.ip_pools_info['host'], self.ip_pools_info['port'])
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

        with open(path + '/manifest.json', 'w') as f:
            f.write(self.get_manifest_content())
        with open(path + '/background.js', 'w') as f:
            f.write(self.get_background_content())

        return os.path.abspath(path)

    def get_extension_file_path(self):
        '''
        从.zip文件中读取插件, 再返回插件路径
        :return:
        '''
        path = "{0}/{1}_{2}.zip".format(self.extension_dir, self.ip_pools_info['host'], self.ip_pools_info['port'])
        if os.path.exists(path):
            os.remove(path)

        zf = ZipFile(path, mode='w')
        zf.writestr('manifest.json', self.get_manifest_content())
        zf.writestr('background.js', self.get_background_content())
        zf.close()

        return os.path.abspath(path)

    def get_manifest_content(self):
        '''
        mainfest.json内容
        :return:
        '''
        return '''
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        '''

    def get_background_content(self):
        '''
        background.js内容(关键内容)
        :return:
        '''
        return '''
        chrome.proxy.settings.set({{
            value: {{
                mode: "fixed_servers",
                rules: {{
                    singleProxy: {{
                        scheme: "{0}",
                        host: "{1}",
                        port: {2}
                    }},
                    bypassList: ["foobar.com"]
                }}
            }},
            scope: "regular"
        }}, function() {{}});

        chrome.webRequest.onAuthRequired.addListener(
            function (details) {{
                return {{
                    authCredentials: {{
                        username: "{3}",
                        password: "{4}"
                    }}
                }};
            }},
            {{ urls: ["<all_urls>"] }},
            [ 'blocking' ]
        );
        '''.format(self.ip_pools_info['schema'], self.ip_pools_info['host'], self.ip_pools_info['port'], self.ip_pools_info['username'], self.ip_pools_info['password'])

def test_fz_driver_obj():
    """
    TEST 测试driver对象
    :return:
    """
    driver = None
    try:
        driver = BaseDriver(
            type=FIREFOX,
            executable_path=FIREFOX_DRIVER_PATH,
            ip_pool_type=tri_ip_pool,
            headless=False,
            load_images=True,)
        url = 'https://www.baidu.com'
        driver.get_url_body(url=url)
        search_input = driver.find_element(
            by=By.CSS_SELECTOR,
            value='input#kw')
        print('search_input:{}'.format(search_input))

        search_input.send_keys('阿发')
        driver.find_element(
            by=By.CSS_SELECTOR,
            value='input#su').click()
        driver.back()

        old_window_handle = driver.current_window_handle
        print('current_window_handle:{}'.format(old_window_handle))
        print('window_handles:{}'.format(driver.window_handles))

        # TODO driver新开窗口的方法, 通过执行js来新开一个窗口
        new_tab_window_js = 'window.open("https://www.sogou.com")'
        driver.execute_async_script(script=new_tab_window_js)
        print('window_handles:{}'.format(driver.window_handles))

        for window_handle in driver.window_handles:
            # 轮询handle
            print('switch to: {}'.format(window_handle))
            driver.switch_to_window(window_name=window_handle)
            print('current_window_handle: {}'.format(driver.current_window_handle))

        sleep(10)

    except Exception as e:
        print(e)

    finally:
        try:
            del driver
        except:
            pass

# test_fz_driver_obj()
