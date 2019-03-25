# coding:utf-8

'''
@author = super_fazai
@File    : requires.py
@Time    : 2016/8/3 12:59
@connect : superonesfazai@gmail.com
'''

install_requires = [
    'ipython',
    'wheel',
    'utils',
    'db',
    'greenlet==0.4.14',     # 之前0.4.13, 改成0.4.14(gevent依靠)
    'pytz',
    'pysocks',              # requests 进行socks代理必备!
    'requests',
    'requests_oauthlib',
    'selenium==3.8.0',      # 3.8.1及其以上版本不支持phantomjs了
    'uvloop',               # asyncio默认事件循环替代品
    'asyncio',
    'psutil',
    'pyexecjs',
    'setuptools',
    'colorama',
    'twine',
    'numpy',
    'pprint',
    'chardet',
    'bs4',
    'scrapy',
    'demjson',
    'gevent',
    'aiohttp',
    'eventlet',             # celery改变单个worker并发量必备库
    'celery',
    'flower',               # web工具，用于监视和管理celery集群。
    'jsonpath',
    'flask',
    'flask_login',
    'mitmproxy',            # shell 抓包代理
    'pyexcel',
    'pyexcel-xlsx',
    'fabric',               # 旨在通过SSH远程执行shell命令
    'furl',                 # 可轻松解析和操作URL
    'yarl',
    'prettytable',
    'xlrd',
    'jieba',                # 旨在做最好用的中文分词
    'scikit-image',         # 图像处理
    'appium-python-client',
    'python-docx',
    'Jinja2',
    'elasticsearch',
    'elasticsearch_dsl',
    'salt',                 # 为大规模复杂系统管理提供软件, 同步控制百万台服务器
    'pika',                 # rabbitmq客户端库
    'items',
    'scapy',                # 功能强大的基于Python的交互式数据包操作程序和库
    'scapy-http',
    'baidu-aip',
    'pytesseract',
    'scrapy-splash',
    'opencv-python',
    'twilio',               # 免费发短信
    'fonttools',            # 用于操作字体的库, eg:爬虫中字形识别
    'xmltodict',
    'python-dateutil',
    'ftfy',                 # 超级强大的unicode文本工具
    'tenacity',             # 强大的python重试库
    'pyzbar',               # 二维码识别库, 安装前提:(ubuntu: sudo apt-get install libzbar-dev | mac: brew install zbar)
    'termcolor',            # shell颜色化输出
    'pypinyin',             # 汉字转拼音包
    'bitarray',             # bloom 需要
    'click',                # shell交互

    # db
    'pymssql',
    'sqlalchemy',
    'pymongo',
    'redis',
    'mongoengine',          # mongo engine

    # TODO 减少依赖
    # 'stem',                 # 操作tor
    # 'jupyter',
    # 'ipywidgets',           # jupyter笔记本和ipython内核的交互式HTML小部件
    # 'matplotlib',
    # 'shadowsocks',
    # 'wget',
    # 'fake-useragent',       # 随机user-agent
    # 'web.py==0.40.dev1',    # IPProxyPool的依赖, 现弃用
    # 'pygame',
    # 'pandas',
    # 'geopandas',            # 向pandas对象添加地理数据支持
    # 'ray',                  # 一个灵活的高性能分布式执行框架
    # 'Flask-APScheduler',    # flask的定时任务库
    # 'newspaper3k',          # 文章提取
    # 'wordcloud',            # 词云
    # 'sip',
    # 'pyqt5',
    # 'bokeh',                # 一个用于Python的交互式可视化库，可在现代Web浏览器中实现美观且有意义的数据可视化呈现
    # 'requests-html',        # requests的html解析器 for human, 但是必须python >= 3.6
    # 'pycurl==7.43.0.1',
]