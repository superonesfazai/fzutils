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
from ..fzutils.spider.fz_requests import Requests
from ..fzutils.common_utils import json_2_dict

# from fzutils.spider.fz_requests import Requests
# from fzutils.common_utils import json_2_dict

__all__ = [
    'JiMa99Smser',              # 集码99的短信验证码服务
]

class JiMa99Smser(object):
    """
    集码99的短信验证码服务
    API doc: http://www.jima99.com/APItool.htm
    """
    def __init__(self, username, pwd, use_proxy=False):
        '''
        :param username: 用户名
        :param pwd: 密码
        :param use_proxy: 是否使用proxy
        '''
        self.username = username
        self.pwd = pwd
        self.use_proxy = use_proxy
        self.token = ''             # 每次成功登陆会返回一个token值

    def _login(self) -> bool:
        '''
        登陆api
        :return:
        '''
        # http://www.jima99.com:9180/service.asmx/UserLoginStr?name=帐户名&psw=密码
        url = 'http://www.jima99.com:9180/service.asmx/UserLoginStr'
        params = (
            ('name', self.username),
            ('psw', self.pwd),
        )
        body = Requests.get_url_body(url=url, params=params, use_proxy=self.use_proxy)
        self.token = body
        print('获取到token: {}'.format(self.token))
        if body == '':
            return False

        return True

    def _get_the_specified_card_num(self, project_num:int, operator_type:int=1) -> str:
        '''
        获取指定卡商号码api
        :param project_num: 申请到的项目编号, 未申请则返回'-8'
        :param operator_type: 号码类型
        :return:
        '''
        if self.token == '':
            print('获取失败, 账户未登录! token值为空!')
            return ''

        # http://www.jima99.com:9180/service.asmx/RjGetKsHMStr?token=登陆令牌&xmid=项目编号&sl=号码数量&lx=号码类型&a1=省份&a2=城市&ks=卡商Id编号&rj=作者帐户Id
        url = 'http://www.jima99.com:9180/service.asmx/RjGetKsHMStr'
        params = (
            ('token', self.token),      # 登陆令牌 字符型 UserLoginStr登陆接口时返回的token
            ('xmid', project_num),      # 项目编号 数值型
            ('sl', 10),                 # 手机号码数量 数值型 要获取号码数量，最大10
            ('lx', operator_type),      # 号码类型 数值型 lx=0是不限运营商，1是移动号码，2是联通号码，3是电信号码，4是外国号码，130到189 是指定只获取指定号段，如：lx=136 是指定只获取分配136号码
            ('a1', ''),                 # 省份 字符型 非必填可为空，获取指定省份的号码（代码调用接口时用utf-8编码）
            ('a2', ''),                 # 城市 字符型 非必填可为空，获取指定城市的号码（代码调用接口时用utf-8编码）
            ('ks', 0),                  # 卡商id编号 数值型 如果不需要获取指定卡商号码，可以填：0
            ('rj', 0),                  # 作者账户id 数值型 该id用来标识计算作者提成，如果不需要可填：0
        )
        body = Requests.get_url_body(url=url, params=params, use_proxy=self.use_proxy)
        if body == '':
            print('获取到body为空值!')

        return body

    def __del__(self):
        collect()

# with open('/Users/afa/myFiles/pwd/jima99_pwd.json', 'r') as f:
#     jima_info = json_2_dict(f.read())
# _ = JiMa99Smser(username=jima_info['username'], pwd=jima_info['pwd'])
# _._login()
# body = _._get_the_specified_card_num(project_num=200)
# print(body)
