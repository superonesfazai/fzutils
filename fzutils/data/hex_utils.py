# coding:utf-8

'''
@author = super_fazai
@File    : hex_utils.py
@connect : superonesfazai@gmail.com
'''

"""
进制转换 utils
"""

__all__ = [
    'int_to_8_digit_sixteen_digit_num',         # 整数转换为8位十六进制数
]

def int_to_8_digit_sixteen_digit_num(i:int) -> str:
    '''
    整数转换为8位十六进制数
    :param i:
    :return:
    '''
    hexrep = format(i,'08x')
    thing = ""
    for i in [3, 2, 1, 0]:
        thing += hexrep[2*i:2*i+2]

    return thing
