# -*- coding: UTF-8 -*-

import time

import Logger
from DefaultManager import DefaultManager
from ThreadPoolManager import ThreadPoolManager
''' 
启动类：爬虫启动类
 '''


class Starter():
    # 日志
    logger = Logger.Logger(
        logname='Log_' + time.strftime("%Y-%m-%d") + '.log',
        loglevel=1,
        logger="Starter.py").getlog()

    # 启动方法
    def start():
        # DefaultManager().dispatch()
        ThreadPoolManager().dispatch()

    if __name__ == "__main__":
        start()
