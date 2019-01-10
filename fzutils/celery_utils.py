# coding:utf-8

'''
@author = super_fazai
@File    : celery_utils.py
@connect : superonesfazai@gmail.com
'''

"""
celery常用函数
"""

from time import time
from celery import Celery
from celery.utils.log import get_task_logger

__all__ = [
    'init_celery_app',              # 初始化一个celery对象
    '_get_celery_async_results',    # 得到celery worker的处理结果集合
]

def init_celery_app(name='proxy_tasks',
                    broker='redis://127.0.0.1:6379',
                    backend='redis://127.0.0.1:6379/0',
                    celeryd_max_tasks_per_child=500) -> Celery:
    '''
    初始化一个celery对象
    :return:
    '''
    app = Celery(
        name,               # 创建一个celery实例, 名叫name
        broker=broker,      # 指定消息中间件，用redis
        backend=backend     # 指定存储用redis
    )
    app.conf.update(
        CELERY_TIMEZONE='Asia/Shanghai',                            # 指定时区, 默认是'UTC'
        CELERY_ACKS_LATE=True,
        CELERY_ACCEPT_CONTENT=['pickle', 'json'],                   # 注意: 'pickle'是一种Python特有的自描述的数据编码, 可序列化自定义对象
        CELERY_TASK_SERIALIZER='pickle',
        CELERY_RESULT_SERIALIZER='pickle',
        CELERYD_FORCE_EXECV=True,
        # CELERYD_HIJACK_ROOT_LOGGER=False,                         # 想要用自己的logger, 则设置为False
        CELERYD_MAX_TASKS_PER_CHILD=celeryd_max_tasks_per_child,    # 长时间运行Celery有可能发生内存泄露，可以像下面这样设置, 这个表示每个工作的进程／线程／绿程 在执行 n 次任务后，主动销毁，之后会起一个新的。主要解决一些资源释放的问题。
        CELERY_TASK_RESULT_EXPIRES=60*60,                           # task result过期时间 单位秒
        BROKER_HEARTBEAT=0,)

    return app

async def _get_celery_async_results(tasks:list) -> list:
    '''
    得到celery worker的处理结果集合
    :param tasks: celery的tasks任务对象集
    :return:
    '''
    all = []
    success_num = 1
    s_time = time()
    while len(tasks) > 0:
        for r_index, r in enumerate(tasks):
            try:
                if r.ready():
                    try:
                        all.append(r.get(timeout=2, propagate=False))
                        print('\r--->>> success_num: {}'.format(success_num), end='', flush=True)
                    except TimeoutError:
                        pass
                    success_num += 1
                    try:
                        tasks.pop(r_index)
                    except:
                        pass
                else:
                    pass
            except Exception as e:
                # redis.exceptions.TimeoutError: Timeout reading from socket
                print(e)
                return []

    else:
        pass
    time_consume = time() - s_time
    print('\n执行完毕! 此次耗时 {} s!'.format(round(float(time_consume), 3)))

    return all

