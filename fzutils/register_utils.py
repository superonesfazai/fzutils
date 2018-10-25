# coding:utf-8

'''
@author = super_fazai
@File    : register_utils.py
@connect : superonesfazai@gmail.com
'''

"""
批量注册工具 utils
"""

from gc import collect
from time import sleep
from ..fzutils.spider.fz_requests import Requests
from ..fzutils.common_utils import json_2_dict

# from fzutils.spider.fz_requests import Requests
# from fzutils.common_utils import json_2_dict

__all__ = [
    'YiMaSmser',                # 易码平台的短信验证码服务
]

class YiMaSmser(object):
    """
    易码平台的短信验证码服务(http://www.51ym.me)(密码不修改token不变)
    api doc: http://www.51ym.me/User/apidocs.html#login
    """
    def __init__(self, username, pwd, use_proxy=False):
        self.username = username
        self.pwd = pwd
        self.token = ''
        self.base_url = 'http://api.fxhyd.cn/UserInterface.aspx'
        self.use_proxy = use_proxy

    def _login(self) -> bool:
        '''
        登陆
        :return:
        '''
        # http://api.fxhyd.cn/UserInterface.aspx?action=login&username=你的账号&password=你的密码
        params = (
            ('action', 'login'),
            ('username', self.username),
            ('password', self.pwd),
        )
        body = Requests.get_url_body(url=self.base_url, params=params, use_proxy=self.use_proxy)
        # print(body)
        if body == '':
            print('获取到的body为空值!')
            return False

        _ = body.split('|')
        try:
            if _[0] == 'success':
                self.token = _[1]
                return True
            else:
                raise IndexError
        except IndexError:
            return False

    def _is_login(self) -> bool:
        '''
        是否登陆，未登录则进行登陆
        :return:
        '''
        login_res = True
        if self.token == '':
            login_res = self._login()

        if not login_res:
            print('account登陆失败!')

        return login_res

    def _get_account_info(self) -> dict:
        '''
        获取当前账户信息
        :return:
        '''
        # http://api.fxhyd.cn/UserInterface.aspx?action=getaccountinfo&token=TOKEN
        if not self._is_login():
            return {}

        params = (
            ('action', 'getaccountinfo'),
            ('token', self.token),
        )
        body = Requests.get_url_body(url=self.base_url, params=params, use_proxy=self.use_proxy)
        # print(body)     # success|用户名|账户状态|账户等级|账户余额|冻结金额|账户折扣|获取号码最大数量
        _ = body.split('|')
        res = {}
        try:
            res = {
                'res': _[0],                # 请求结果
                'username': _[1],           # 用户名
                'account_state': _[2],      # 账户状态
                'account_level': _[3],      # 账户等级
                'account_balance': _[4],    # 账户余额
                'freezing_amount': _[5],    # 冻结的金额
                'account_discounts': _[6],  # 账户的折扣
                'max_phone_num': _[7],      # 获取号码最大数量
            }
        except IndexError as e:
            print(e)

        return res

    def _get_phone_num(self, project_id, exclude_no='', province='') -> str:
        '''
        获取手机号码(获取是不收费的)
        :param project_id: 项目编号 http://www.51ym.me/User/MobileItemList.aspx中查找关键字
        :param exclude_no: 排除号段 不获取170、171和188号段的号码，则该参数为170.171.180，每个号段必须是前三位，用小数点分隔。
        :param province: 省代码 号码归属地的省份代码，省市代码表。
        :return: '' | 获取到的手机号
        '''
        # http://api.fxhyd.cn/UserInterface.aspx?action=getmobile&token=TOKEN&itemid=项目编号&excludeno=排除号段
        if not self._is_login():
            return ''

        params = (
            ('action', 'getmobile'),
            ('token', self.token),
            ('itemid', str(project_id)),
            ('excludeno', str(exclude_no)),
            ('province', str(province)),
        )
        body = Requests.get_url_body(url=self.base_url, params=params, use_proxy=self.use_proxy)
        # print(body)

        _ = body.split('|')
        if _[0] == 'success':
            return _[1]
        else:
            return ''

    def _get_sms(self, phone_num, project_id, release='1', timeout=66) -> str:
        '''
        获取手机号对应的短信
        :param phone_num: 手机号码
        :param project_id: 项目编号
        :param release: 自动释放号码标识符 该参数值为1时，获取到短信的同时系统将自己释放该手机号码。若要继续使用该号码，请勿带入该参数。 设置为''
        :param timeout: 短信验证码内容超时等待时长
        :return:
        '''
        # http://api.fxhyd.cn/UserInterface.aspx?action=getsms&token=TOKEN&itemid=项目编号&mobile=手机号码&release=1
        if not self._is_login():
            return ''

        params = (
            ('action', 'getsms'),
            ('token', self.token),
            ('itemid', str(project_id)),
            ('mobile', str(phone_num)),
            ('release', release),
        )
        _t = 0
        index = 1
        while True:
            if _t >= timeout:
                print('超时退出!!')
                return ''

            body = Requests.get_url_body(url=self.base_url, params=params, use_proxy=self.use_proxy)
            _ = body.split('|')
            if _[0] == 'success':
                return _[1]
            else:
                print('{} try get sms content...sleeping 5s...'.format(index))
                print(body)
                sleep(5)
            _t += 5
            index += 1

    def _send_sms(self, phone_num, project_id, content:str, receive_phone_num='') -> bool:
        '''
        发送短信
        :param phone_num: 手机号
        :param project_id: 项目id
        :param content: 短信内容
        :param receive_phone_num: 接收的短信的手机号，默认为空值
        :return: True 只代表成功提交发送任务，不代表短信已经成功发送，获取发送结果请调用“获取短信发送结果”接口。
        '''
        # http://api.fxhyd.cn/UserInterface.aspx?action=sendsms&token=TOKEN&itemid=项目编号&mobile=手机号码&sms=发送内容
        if not self._is_login():
            return False

        params = (
            ('action', 'sendsms'),
            ('token', self.token),
            ('itemid', str(project_id)),
            ('mobile', str(phone_num)),
            ('sms', content),
            ('number', str(receive_phone_num)),
        )
        body = Requests.get_url_body(url=self.base_url, params=params, use_proxy=self.use_proxy)
        _ = body.split('|')
        if _[0] == 'success':
            return True
        else:
            return False

    def _get_send_sms_res(self, phone_num, project_id) -> bool:
        '''
        获取发短信结果
        :param phone_num: 发短信的手机号
        :param project_id: 项目编号
        :return:
        '''
        # http://api.fxhyd.cn/UserInterface.aspx?action=getsendsmsstate&token=TOKEN&itemid=项目编号&mobile=手机号码
        if not self._is_login():
            return False

        params = (
            ('action', 'getsendsmsstate'),
            ('token', self.token),
            ('itemid', str(project_id)),
            ('mobile', str(phone_num)),
        )
        body = Requests.get_url_body(url=self.base_url, params=params, use_proxy=self.use_proxy)
        _ = body.split('|')
        if _[0] == 'success':
            return True
        else:   # 等待发送：3002 | 正在发送：3003 | 发送失败：3004
            return False

    def _release_phone_num(self, phone_num, project_id) -> bool:
        '''
        释放手机号码(注意: 如果号码不再使用请及时释放，否则你未释放的号码达到获取号码上限后将不能获取到新的号码。)
        :param phone_num: 被释放的手机号
        :param project_id: 项目编号
        :return:
        '''
        # http://api.fxhyd.cn/UserInterface.aspx?action=release&token=TOKEN&itemid=项目编号&mobile=手机号码
        if not self._is_login():
            return False

        params = (
            ('action', 'release'),
            ('token', self.token),
            ('itemid', str(project_id)),
            ('mobile', str(phone_num)),
        )
        body = Requests.get_url_body(url=self.base_url, params=params, use_proxy=self.use_proxy)
        _ = body.split('|')
        if _[0] == 'success':
            return True
        else:
            return False

    def __del__(self):
        collect()

# @外部调用
# 测试批量注册微博账号: https://passport.sina.cn/signup/signup?entry=wapsso&r=https%3A%2F%2Fsina.cn%2Findex%2Fsettings%3Fvt%3D4%26pos%3D108
# with open('/Users/afa/myFiles/pwd/yima_pwd.json', 'r') as f:
#     yima_info = json_2_dict(f.read())
# _ = YiMaSmser(username=yima_info['username'], pwd=yima_info['pwd'])
#
# # project_id = 35
# project_id = 715
# while True:
#     phone_num = _._get_phone_num(project_id=project_id)
#     print(phone_num)
#     a = input('是否可用: ')
#     if a == 'y':
#         break
#
# print('\n未注册的: {}'.format(phone_num))
# sms_res = _._get_sms(phone_num=phone_num, project_id=project_id)
# print(sms_res)
# res = _._get_account_info()
# from pprint import pprint
# pprint(res)