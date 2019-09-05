# -*- coding: UTF-8 -*-
import json
import random
import threading
import time
import traceback

import requests

import Logger
''' 
代理工具类：从IP代理提供商处更新IP
使用单例模式
 '''


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class ProxyUtil():
    # 日志
    logger = Logger.Logger(
        logname='Log_' + time.strftime("%Y-%m-%d") + '.log',
        loglevel=1,
        logger="ProxyUtil.py").getlog()
    # 线程锁
    lock = threading.Lock()
    # 默认代理IP时间间隔15s
    TIME_INTERVAL = 15
    # http代理列表
    http_proxies = []

    # 定时任务
    def task(self):
        self.__update_proxy()
        timer = threading.Timer(self.TIME_INTERVAL, self.task)
        timer.setDaemon(True)
        timer.start()

    # 更新IP代理
    def __update_proxy(self):
        ''' 
        每TIME_INTERVAL调用指定IP代理提供商API接口获取代理IP
         '''
        try:
            self.lock.acquire()

            self.logger.info('当前时间：' + str(time.time()))

            # 一次获取80个IP
            response = requests.get(
                'http://www.bugng.com/api/getproxy/json?num=80&anonymity=1&type=0',
                # proxies=self.get_proxy(),
                timeout=3)
            # 判断状态码200 OK
            if response.status_code == 200:
                result = response.text

            result_jsonObj = json.loads(result)
            if result_jsonObj['code'] == 0:
                result_data = result_jsonObj['data']
                result_proxy_list = result_data['proxy_list']
                for proxy in result_proxy_list:
                    self.http_proxies.append({'http': 'http://' + proxy})
            # 设为默认值15S
            self.TIME_INTERVAL = 15
        # except IndexError:
        #     self.logger.error('代理为空：' + traceback.format_exc())
        except json.decoder.JSONDecodeError:
            self.logger.error('提取过于频繁：' + traceback.format_exc())
            # time.sleep(300)
            self.TIME_INTERVAL = 300
        except BaseException:
            self.logger.error('提取API出错：' + traceback.format_exc())
            # time.sleep(300)
            self.TIME_INTERVAL = 300
        finally:
            self.lock.release()
        return None

    # 获得IP代理
    def get_proxy(self):
        try:
            if self.http_proxies:
                return random.choice(self.http_proxies)
        except BaseException:
            self.logger.error('获取代理IP出错：' + traceback.format_exc())
        return None

    # 删除IP代理
    def remove_proxy(self, ip):
        try:
            if ip in self.http_proxies:
                self.http_proxies.remove(ip)
        except BaseException:
            self.logger.error('删除代理IP出错：' + traceback.format_exc())
