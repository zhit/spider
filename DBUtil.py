# -*- coding: UTF-8 -*-
import threading
import time
import traceback

import psycopg2

import Logger

# 日志
logger = Logger.Logger(
    logname='Log_' + time.strftime("%Y-%m-%d") + '.log',
    loglevel=1,
    logger="DBUtil.py").getlog()
'''
该类为对数据库操作封装的工具类
 '''


class DBUtil():
    # 数据库名
    DATABASE = "hc"
    # 用户名
    USER = "feihua"
    # 密码
    PASSWORD = "feihua"
    # 主机
    HOST = "127.0.0.1"
    # 端口
    PORT = "5432"
    # 线程锁
    lock = threading.Lock()

    # 实例化一个数据库对象
    def __init__(self):
        pass

    # 数据库连接
    def __connection(self):
        conn = None
        try:
            conn = psycopg2.connect(
                database=self.DATABASE,
                user=self.USER,
                password=self.PASSWORD,
                host=self.HOST,
                port=self.PORT)
        except BaseException:
            logger.error('获得数据库连接出错：' + traceback.format_exc())
        return conn

    # 数据库关闭
    def __close(self, cur, conn):
        try:
            cur.close()
            conn.close()
        except BaseException:
            logger.error('关闭数据库连接出错：' + traceback.format_exc())

    # 查询一个
    def query_one(self, sql, params=None):
        try:
            # 获得锁
            self.lock.acquire()
            conn = self.__connection()
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            row = cur.fetchone()
            if row:
                return str(row[0])
        except BaseException:
            logger.error('查询出错：' + traceback.format_exc())
        finally:
            self.__close(cur, conn)
            # 释放锁
            self.lock.release()
        return None

    # 查询列表
    def query_list(self, sql, params=None):
        result = []
        try:
            # 获得锁
            self.lock.acquire()
            conn = self.__connection()
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            rows = cur.fetchall()
            if rows:
                for row in rows:
                    cols = []
                    for col in row:
                        # 所有结果转为字符串
                        cols.append(str(col))
                    result.extend([cols])
                return result
        except BaseException:
            logger.error('查询列表出错：' + traceback.format_exc())
        finally:
            self.__close(cur, conn)
            # 释放锁
            self.lock.release()
        return result

    # 插入
    def insert(self, sql, params=None):
        try:
            # 获得锁
            self.lock.acquire()
            conn = self.__connection()
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            conn.commit()
            row = cur.fetchone()
            if row:
                return str(row[0])
        except BaseException:
            logger.error('插入出错：' + traceback.format_exc())
        finally:
            self.__close(cur, conn)
            # 释放锁
            self.lock.release()
        return None

    # 更新
    def update(self, sql, params=None):
        try:
            # 获得锁
            self.lock.acquire()
            conn = self.__connection()
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            conn.commit()
        except BaseException:
            logger.error('更新出错：' + traceback.format_exc())
        finally:
            self.__close(cur, conn)
            # 释放锁
            self.lock.release()
        return None

    # 删除
    def delete(self, sql, params=None):
        pass
