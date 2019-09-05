# -*- coding: UTF-8 -*-
import json
import random
import re
import time
import traceback
from Cookie import Cookie

import requests
import urllib3

import Logger
from ProxyUtil import ProxyUtil

# from Proxy import Proxy
''' 
爬虫类：爬取指定URL
 '''


class Spider():
    # 日志
    logger = Logger.Logger(
        logname='Log_' + time.strftime("%Y-%m-%d") + '.log',
        loglevel=1,
        logger="Spider.py").getlog()
    # Cookie文件路径
    cookie = 'cookie.txt'

    # 爬取指定请求
    def spider_URL(self,
                   url,
                   params=None,
                   headers=None,
                   cookies=None,
                   is_proxies=False,
                   is_reconnect=False,
                   encode=None):
        # 结果
        result = None
        try:
            # 默认代理为None
            proxies = None
            # 若headers为None 加载默认配置
            if headers is None:
                headers = self.__random_header(self.__headers())
            # 若cookies为None 加载默认配置
            # if cookies is None:
            #     cookies = Cookie.load(self.cookie)
            # 若is_proxies为True 加载代理配置
            if is_proxies is True:
                # proxies = self.__random_proxie()
                proxies = ProxyUtil().get_proxy()
            '''
            NOTE 发起请求有两种方式
            1：普通requests.get/post
            2：使用session
            '''

            # 方式1：
            # 普通请求 超时时间8s
            response = requests.get(
                url=url,
                params=params,
                headers=headers,
                cookies=cookies,
                proxies=proxies,
                timeout=8)

            # 方式2:
            ''' # 使用sessios保持会话的请求
            session = requests.session()
            # 更新headers参数到session
            session.headers.update(headers)
            # 发起请求
            response = session.get(
                url=url,
                params=params,
                headers=headers,
                cookies=cookies,
                proxies=proxies) '''

            # 判断状态码200 OK
            if response.status_code == 200:
                # 编码
                if encode:
                    response.encoding = encode
                # 保存cookies
                # if response.cookies:
                #     Cookie.save(response.cookies, 'cookie.txt')
                # 爬取结果
                result = response.text
            if response.status_code == 403:
                self.logger.error('403,连接被拒绝')
                # 403 错误需要等待一段时间后再抓取
                # time.sleep(600)
                # 403 错误需要更换IP
                ProxyUtil().remove_proxy(proxies)
                return result
            if response.status_code == 404:
                self.logger.error('404,您访问的页面不存在')
                return result
            if response.status_code == 500:
                self.logger.error('500,服务器错误')
                return result
            # 判断当前返回url是否为登录链接
            login = re.match(r'sso.hc360.com', response.url)
            if login:
                self.logger.error('糟糕，需要登录了...')
                time.sleep(600)
        except urllib3.exceptions.MaxRetryError:
            self.logger.error('超过最大连接数：' + traceback.format_exc())
            # 从代理列表中清除掉该IP
            ProxyUtil().remove_proxy(proxies)
            # 重连一次
            if is_reconnect is False:
                # result = self.spider_URL(url=url, is_reconnect=True)
                result = self.spider_URL(
                    url=url, is_reconnect=True, is_proxies=True)
        except requests.exceptions.ReadTimeout:
            self.logger.error('读取超时：' + traceback.format_exc())
            # 从代理列表中清除掉该IP
            ProxyUtil().remove_proxy(proxies)
            # 重连一次
            if is_reconnect is False:
                # result = self.spider_URL(url=url, is_reconnect=True)
                result = self.spider_URL(
                    url=url, is_reconnect=True, is_proxies=True)
        except urllib3.exceptions.ConnectTimeoutError:
            self.logger.error('连接超时：' + traceback.format_exc())
            # 从代理列表中清除掉该IP
            ProxyUtil().remove_proxy(proxies)
            # 重连一次
            if is_reconnect is False:
                # result = self.spider_URL(url=url, is_reconnect=True)
                result = self.spider_URL(
                    url=url, is_reconnect=True, is_proxies=True)
        except requests.exceptions.ConnectTimeout:
            self.logger.error('连接超时：' + traceback.format_exc())
            # 从代理列表中清除掉该IP
            ProxyUtil().remove_proxy(proxies)
            # 重连一次
            if is_reconnect is False:
                # result = self.spider_URL(url=url, is_reconnect=True)
                result = self.spider_URL(
                    url=url, is_reconnect=True, is_proxies=True)
        except requests.exceptions.ProxyError:
            self.logger.error('连接代理出错：' + traceback.format_exc())
            # 从代理列表中清除掉该IP
            ProxyUtil().remove_proxy(proxies)
            # 代理出错则使用本机再次访问
            # 重连一次
            if is_reconnect is False:
                # result = self.spider_URL(url=url, is_reconnect=True)
                result = self.spider_URL(
                    url=url, is_reconnect=True, is_proxies=True)
        except urllib3.exceptions.ProtocolError:
            self.logger.error('远程主机强迫关闭了一个现有的连接：' + traceback.format_exc())
            # 从代理列表中清除掉该IP
            ProxyUtil().remove_proxy(proxies)
            # 重连一次
            if is_reconnect is False:
                # result = self.spider_URL(url=url, is_reconnect=True)
                result = self.spider_URL(
                    url=url, is_reconnect=True, is_proxies=True)
        except requests.exceptions.ConnectionError:
            self.logger.error('远程主机强迫关闭了一个现有的连接：' + traceback.format_exc())
            # 从代理列表中清除掉该IP
            ProxyUtil().remove_proxy(proxies)
            # 重连一次
            if is_reconnect is False:
                # result = self.spider_URL(url=url, is_reconnect=True)
                result = self.spider_URL(
                    url=url, is_reconnect=True, is_proxies=True)
        except ConnectionResetError:
            self.logger.error('连接被重置：' + traceback.format_exc())
            # 从代理列表中清除掉该IP
            ProxyUtil().remove_proxy(proxies)
            # 重连一次
            if is_reconnect is False:
                # result = self.spider_URL(url=url, is_reconnect=True)
                result = self.spider_URL(
                    url=url, is_reconnect=True, is_proxies=True)
        except BaseException:
            self.logger.error('爬取' + url + '出错：' + traceback.format_exc())
        return result

    # 伪造Headers
    def __headers(self, params=None):
        headers = {}
        headers[
            'User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3086.0 Safari/537.36"
        headers['accept-language'] = 'zh-CN,zh;q=0.8'
        ''' 
        配置的以下参数是避免被反爬虫阻止
        '''
        # 关闭连接
        headers['Connection'] = 'close'

        # 存在参数字典
        if params:
            if isinstance(params, dict):
                keys = params.keys()
                for key in keys:
                    headers[key] = params[key]
        return headers

    # 随机userAgent
    def __random_header(self, headers):
        # 所有主流PC端user-Agent
        user_agents = (
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3086.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C; .NET4.0E; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv,2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
            'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')
        # 随机取一个
        headers['User-Agent'] = random.choice(user_agents)
        return headers

    # 默认配置
    def __conf(self, headers, cookies, proxies, encode):
        pass
