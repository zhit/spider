# -*- coding: UTF-8 -*-
import math
import threading
import time
import traceback

import threadpool

import Logger
from DBUtil import DBUtil
from Interpreter import Interpreter
from ProxyUtil import ProxyUtil
from Spider import Spider
'''
线程池管理类：处理抓取、解析、保存的调度处理
 '''


class ThreadPoolManager():
    # 日志
    logger = Logger.Logger(
        logname='Log_' + time.strftime("%Y-%m-%d") + '.log',
        loglevel=1,
        logger="ThreadPoolManager.py").getlog()
    # 网站首页
    URL = 'http://www.hc360.com/'
    lock = threading.Lock()

    # 调度
    def dispatch(self):
        # 程序启动时间
        time_start = time.time()

        # 启动代理类定时任务
        proxy_thread = threading.Thread(
            target=ProxyUtil().task, name='proxy_thread')
        # 启动线程池爬取任务
        task_thread = threading.Thread(
            target=self.task_pool, name='task_thread')

        proxy_thread.start()
        task_thread.start()

        proxy_thread.join()
        task_thread.join()

        self.logger.info('程序运行耗时：' + str(time.time() - time_start))

    # 线程池爬取任务
    def task_pool(self):
        # 爬取所有商城详细信息
        # stores = self.query_store()
        # 爬取所有产品详细信息
        products = self.query_products()

        # 创建两个线程池数量分别为10
        # store_pool = threadpool.ThreadPool(10)
        product_pool = threadpool.ThreadPool(20)
        # store_requests = threadpool.makeRequests(self.spider_store_details,
        #                                          stores)
        # [store_pool.putRequest(req) for req in store_requests]
        product_requests = threadpool.makeRequests(self.spider_product_details,
                                                   products)
        [product_pool.putRequest(req) for req in product_requests]

        # store_pool.wait()
        product_pool.wait()

    # 爬取基本信息

    def spider_basic(self):
        ''' # 爬取分类
        spider_time = time.time()
        self.logger.info('开始爬取：' + self.URL)
        result_category = Spider().spider_URL(url=self.URL)
        self.logger.info('爬取耗时：' + str(time.time() - time_start))

        # 解析分类
        interpreting_time = time.time()
        self.logger.info('开始解析：' + self.URL)
        categorys = Interpreter().interpreting_category(result_category)
        self.logger.info('解析耗时：' + str(time.time() - interpreting_time))

        # 保存分类
        self.save_category(categorys) '''
        # 处理抓取中断
        self.interrupt_handler()
        # 查询未爬取分类保存结果
        categorys_2nd = self.query_category()
        for category_2nd in categorys_2nd:
            # 抓取下一个二级分类休息3秒钟
            time.sleep(10)
            # 解析产品列表page1~page100
            self.spider_product(category_2nd, 1, 101)

    # 爬取产品详情

    def spider_product_details(self, product):

        time.sleep(1)
        try:
            # 爬取产品详情页
            spider_time = time.time()
            self.logger.info('开始爬取：' + product[1])
            result_products = Spider().spider_URL(
                url=product[1], is_proxies=True)
            # self.logger.info('爬取耗时：' + str(time.time() - spider_time))

            # 解析产品详情页
            interpreting_time = time.time()
            self.logger.info('开始解析：' + product[1])
            details = Interpreter().interpreting_product_details(
                result_products)
            # self.logger.info('解析耗时：' + str(time.time() - interpreting_time))
            '''
            # 若产品详情需要再次爬取
            product_bcid = details.get('bcid')
            if product_bcid:
                interpreting_time = time.time()
                xss_filter = 'http://wsdetail.b2b.hc360.com/XssFilter?callback=jQuery&bcid='
                result_product_introduce = Spider().spider_URL(
                    url=xss_filter + product_bcid)
                self.logger.info('开始解析：' + xss_filter + product_bcid)
                details['desc'] = Interpreter(
                ).interpreting_product_details_desc(
                    result_product_introduce)
                # 组装产品详情
                details = Interpreter().assemble_product_details(details)
                self.logger.info('解析耗时：' +
                                    str(time.time() - interpreting_time)) '''
            # 更新产品详情
            self.update_products(product[0], details)
        except BaseException:
            self.logger.error('爬取或更新产品详情出错：' + traceback.format_exc())
            # continue

        # 爬取商城信息详情
    def spider_store_details(self, store):

        time.sleep(1)
        try:
            contacts = None
            # 爬取联系方式页
            spider_time = time.time()
            self.logger.info('开始爬取：' + store[1])
            result_contacts = Spider().spider_URL(
                url=store[1], is_proxies=True)
            self.logger.info('爬取耗时：' + str(time.time() - spider_time))

            # 解析联系方式页
            interpreting_time = time.time()
            self.logger.info('开始解析：' + store[1])
            contacts = Interpreter().interpreting_contact_info(result_contacts)
            self.logger.info('解析耗时：' + str(time.time() - interpreting_time))
            # 爬取联系方式页
            if not contacts:
                spider_time = time.time()
                store[1] += '/shop/company.html'
                self.logger.info('开始爬取：' + store[1])
                result_contacts = Spider().spider_URL(
                    url=store[1], is_proxies=True)
                self.logger.info('爬取耗时：' + str(time.time() - spider_time))

                # 解析联系方式页
                interpreting_time = time.time()
                self.logger.info('开始解析：' + store[1])
                contacts = Interpreter().interpreting_contact_info(
                    result_contacts)
                self.logger.info('解析耗时：' +
                                 str(time.time() - interpreting_time))

            # 更新联系方式
            self.update_contacts(store[0], contacts)
        except BaseException:
            self.logger.error('爬取或更新联系方式出错：' + traceback.format_exc())
        # 一次循环执行完后再次调用本方法查询
        # self.spider_store_details()

        # 抓取指定页产品
    def spider_product(self, category_2nd, start, end):
        # 解析产品列表page1~page100
        for i in range(start, end):
            try:
                # 爬取下一页休息3s
                time.sleep(1)
                # 分三次抓取当前页60个产品
                product_list = []
                for j in range(3):
                    req = category_2nd[1] + '&ap=A&t=1&afadprenum=0&af=1' + '&ee=' + str(
                        i) + '&afadbeg=' + str(60 * (i - 1) + (j * 20) + 1)
                    # 爬取并解析
                    spider_time = time.time()
                    self.logger.info('开始爬取：' + req)
                    result_product_list = Spider().spider_URL(
                        url=req, is_proxies=True)

                    self.logger.info('爬取耗时：' + str(time.time() - spider_time))

                    interpreting_time = time.time()
                    self.logger.info('开始解析：' + req)
                    product_list.extend(Interpreter(
                    ).interpreting_product_list(result_product_list))
                    self.logger.info('解析耗时：' +
                                     str(time.time() - interpreting_time))
                '''
                先爬取所有产品列表信息，后再逐个抓取产品详情及公司信息
                '''
                for product in product_list:
                    # 保存公司信息
                    contact = {}
                    contact['公司名'] = product.get('company')
                    contact['公司主页'] = product.get('homepage')
                    store_id = self.save_contacts(contact)
                    # 保存产品
                    self.save_product(product, category_2nd[0], store_id)
            except BaseException:
                self.logger.error('爬取或解析' + req + '出错：' +
                                  traceback.format_exc())
                continue

    # 保存分类
    def save_category(self, categorys):
        try:
            for industry_key, industry_value in categorys.items():
                INSERT_CATEGORY_INDUSTRY = "INSERT INTO category_industry(category_name) VALUES ('" + industry_key + "') RETURNING category_industry_id"
                INSERT_CATEGORY_TOP = "INSERT INTO category_top(category_name,category_industry_id) VALUES (%s,%s) RETURNING category_top_id"
                INSERT_CATEGORY_2ND = "INSERT INTO category_2nd(category_name,category_href,category_top_id) VALUES (%s,%s,%s) RETURNING category_2nd_id"
                # 保存行业分类 返回行业分类id
                category_industry_id = DBUtil().insert(
                    INSERT_CATEGORY_INDUSTRY)
                for category_top_key, category_top_value in industry_value.items(
                ):
                    # 保存一级分类 返回一级分类id
                    category_top_id = DBUtil().insert(INSERT_CATEGORY_TOP,
                                                      (category_top_key,
                                                       category_industry_id))
                    for category_2nd_key, category_2nd_value in category_top_value.items(
                    ):
                        # 保存二级分类
                        DBUtil().insert(INSERT_CATEGORY_2ND,
                                        (category_2nd_key, category_2nd_value,
                                         category_top_id))
        except BaseException:
            self.logger.error('保存分类出错：' + traceback.format_exc())

    # 保存产品信息
    def save_product(self, product, category, store_id):
        try:
            if (not product) or (not category):
                return None
            result = None
            # img = product.get('img')
            # 如果产品图片少于8张则填充None
            # if len(img) < 8:
            #     img += [None] * (8 - len(img))
            # 通过产品链接查询该产品是否已经存在
            QUERY_PRODUCT_ID = "SELECT product_id FROM product WHERE product_href='" + product.get(
                'href') + "'"
            INSERT_PRODUCT = "INSERT INTO product(product_name,price,quantity_uom_id,currency_uom_id,product_href,product_img_0,product_img_1,product_img_2,product_img_3,product_img_4,product_img_5,product_img_6,product_img_7,description,long_description,category_2nd_id,store_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING product_id"
            result = DBUtil().query_one(QUERY_PRODUCT_ID)
            if result:
                return str(result)
            result = DBUtil().insert(
                INSERT_PRODUCT,
                (product.get('title'), product.get('price'),
                 product.get('unit'), product.get('currency'),
                 product.get('href'), None, None, None, None, None, None, None,
                 None, None, None, category, store_id))
        except BaseException:
            self.logger.error('保存产品信息出错：' + traceback.format_exc())
        return str(result)

    # 保存联系方式
    def save_contacts(self, contacts):
        try:
            result = None
            # 所有联系方式
            name = contacts.get('公司名')
            linkman = contacts.get('联系人')
            homepage = contacts.get('公司主页')
            telephone = contacts.get('电话')
            mobile_phone = contacts.get('手机')
            other_phone = contacts.get('其他电话')
            fax = contacts.get('传真')
            address = contacts.get('地址') or contacts.get('经营地址')
            # 通过主页相同查询判断该商城是否已经存在
            QUERY_STORE_ID = "SELECT store_id FROM store WHERE store_homepage='" + homepage + "'"
            INSERT_STORE = "INSERT INTO store(store_name,store_homepage,linkman,telephone,mobile_phone,other_phone,fax,address) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING store_id"
            result = DBUtil().query_one(QUERY_STORE_ID)
            if result:
                return str(result)
            result = DBUtil().insert(INSERT_STORE,
                                     (name, homepage, linkman, telephone,
                                      mobile_phone, other_phone, fax, address))
        except BaseException:
            self.logger.error('保存联系方式出错：' + traceback.format_exc())
        return str(result)

    # 更新产品详情
    def update_products(self, product_id, products):
        try:
            # 所有产品详情
            imgs = products.get('imgs')
            # 如果产品图片少于8张则填充None
            if len(imgs) < 8:
                imgs += [None] * (8 - len(imgs))
            details = products.get('details')
            UPDATE_PRODUCT = 'UPDATE product SET product_img_0=%s, product_img_1=%s, product_img_2=%s,                         product_img_3=%s, product_img_4=%s, product_img_5=%s,  product_img_6=%s, product_img_7=%s, long_description=%s WHERE product_id=%s'
            DBUtil().update(UPDATE_PRODUCT,
                            (imgs[0], imgs[1], imgs[2], imgs[3], imgs[4],
                             imgs[5], imgs[6], imgs[7], details, product_id))
        except BaseException:
            self.logger.error('更新产品详情出错：' + traceback.format_exc())

    # 更新商城联系人信息
    def update_contacts(self, store_id, contacts):
        try:
            # 所有联系方式
            linkman = contacts.get('联系人')
            telephone = contacts.get('电话')
            mobile_phone = contacts.get('手机') or contacts.get('手机号')
            other_phone = contacts.get('其他电话')
            fax = contacts.get('传真')
            address = contacts.get('地址') or contacts.get('经营地址')
            UPDATE_STORE = 'UPDATE store SET linkman=%s,telephone=%s,mobile_phone=%s,other_phone=%s,fax=%s,address=%s WHERE store_id=%s'
            DBUtil().update(UPDATE_STORE,
                            (linkman, telephone, mobile_phone, other_phone,
                             fax, address, store_id))
        except BaseException:
            self.logger.error('更新联系方式出错：' + traceback.format_exc())

    # 查询未爬取分类
    def query_category(self):
        category_2nd_id = '9999'
        result = []
        LAST_CATEGORY_2ND = 'SELECT category_2nd_id FROM product ORDER BY product_id DESC LIMIT 1'
        LOAD_CATEGORY = 'SELECT category_2nd_id,category_href FROM category_2nd WHERE category_2nd_id>'
        try:
            category_2nd_id = DBUtil().query_one(LAST_CATEGORY_2ND)
            result = DBUtil().query_list(LOAD_CATEGORY + category_2nd_id)
        except BaseException:
            self.logger.error('查询分类出错：' + traceback.format_exc())
        return result

    # 查询数据库最后一个分类现有产品量
    def query_product_count(self):
        result = None
        # 最后一条二级分类产品总数
        LAST_CATEGORY_2ND_COUNT = 'SELECT count(*) FROM product WHERE category_2nd_id=(SELECT category_2nd_id FROM product ORDER BY product_id DESC LIMIT 1)'
        try:
            result = DBUtil().query_one(LAST_CATEGORY_2ND_COUNT)
        except BaseException:
            self.logger.error('查询产品量出错：' + traceback.format_exc())
        return result

    # 查询最后一条产品的二级分类
    def query_category_2nd(self):
        result = []
        # 最后一条二级分类产品总数
        LAST_CATEGORY_2ND = 'SELECT category_2nd_id,category_href FROM category_2nd WHERE category_2nd_id=(SELECT category_2nd_id FROM product ORDER BY product_id DESC LIMIT 1)'
        try:
            result = DBUtil().query_list(LAST_CATEGORY_2ND)
        except BaseException:
            self.logger.error('查询最后一条二级分类出错：' + traceback.format_exc())
        return result

    # 查询所有的产品
    def query_products(self):
        result = []
        LOAD_PRODUCT = 'SELECT product_id,product_href FROM product WHERE product_img_0 IS NULL'
        try:
            result = DBUtil().query_list(LOAD_PRODUCT)
        except BaseException:
            self.logger.error('查询所有产品出错：' + traceback.format_exc())
        return result

    # 查询未抓取商城详情商家
    def query_store(self):
        result = []
        # store_id = '9999'
        # LAST_STORE_ID = 'SELECT store_id FROM store WHERE linkman IS NOT NULL ORDER BY store_id DESC LIMIT 1'
        # LAST_STORE_ID = "SELECT store_id FROM store WHERE store_homepage='http://hcwsteduojm.b2b.hc360.com'"
        LOAD_STORE = "SELECT store_id,store_homepage FROM store WHERE linkman IS NULL ORDER BY store_id ASC"
        # LOAD_STORE = 'SELECT store_id,store_homepage FROM store WHERE linkman IS NULL AND store_id>'
        try:
            # store_id = DBUtil().query_one(LAST_STORE_ID)
            # result = DBUtil().query_list(LOAD_STORE + store_id)
            result = DBUtil().query_list(LOAD_STORE)
        except BaseException:
            self.logger.error('查询现有商家出错：' + traceback.format_exc())
        return result

    # 抓取中断处理
    def interrupt_handler(self):
        try:
            # 最后一个二级分类产品总数
            count = self.query_product_count()
            ''' 查询当前处于第几页 采用向上取整方式 丢弃当前查询不完整的页
            '''
            page_num = math.ceil(int(count) / 60)
            # 最后一个二级分类链接
            last_category_2nd = self.query_category_2nd()
            for i in last_category_2nd:
                # 若存在则执行中断抓取
                if last_category_2nd:
                    self.spider_product(i, page_num, 101)
        except BaseException:
            self.logger.error('抓取中断处理出错：' + traceback.format_exc())
