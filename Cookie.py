# -*- coding: UTF-8 -*-
''' 
Cookie类用于对加载cookie文件和对cookie的写入
 '''
import http.cookiejar
import time

import Logger

# 日志
logger = Logger.Logger(
    logname='Log_' + time.strftime("%Y-%m-%d") + '.log',
    loglevel=1,
    logger="Cookie.py").getlog()


class Cookie():
    @staticmethod
    def save(cookiejar, filename):
        try:
            mozilla_cookiejar = http.cookiejar.MozillaCookieJar()
            for c in cookiejar:
                args = dict(vars(c).items())
                args['rest'] = args['_rest']
                del args['_rest']
                c = http.cookiejar.Cookie(**args)
                mozilla_cookiejar.set_cookie(c)
            mozilla_cookiejar.save(
                filename, ignore_discard=True, ignore_expires=True)
        except BaseException as e:
            logger.error('保存cookie出错' + str(e))

    @staticmethod
    def load(filename):
        try:
            mozilla_cookiejar = None
            mozilla_cookiejar = http.cookiejar.MozillaCookieJar()
            mozilla_cookiejar.load(
                filename, ignore_discard=True, ignore_expires=True)
        except BaseException as e:
            logger.error('加载cookie出错' + str(e))
        return mozilla_cookiejar
