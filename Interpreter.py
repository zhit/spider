# -*- coding: UTF-8 -*-
import decimal
import json
import sys
import time
import traceback

from bs4 import BeautifulSoup

import Logger
from Spider import Spider
''' 
解析类：解析爬虫抓取的数据
 '''


class Interpreter():
    type = sys.getfilesystemencoding()

    # 日志
    logger = Logger.Logger(
        logname='Log_' + time.strftime("%Y-%m-%d") + '.log',
        loglevel=1,
        logger="Interpreter.py").getlog()

    # 解析分类 包含行业分类、一级分类、二级分类 过滤同名分类
    def interpreting_category(self, html_doc):
        try:
            # 行业分类
            category_industry = {}
            # 编码
            doc = BeautifulSoup(html_doc, 'html5lib')
            # 分类div节点
            category_div = doc.find('div', id='category')
            # 该节点下所有分类div节点
            category_list_div = category_div.find_all(
                'div', class_='H_sideBar_list')
            for category in category_list_div:
                # 行业分类
                category_industry_text = category.get('data-name')
                # 一级分类
                category_top_div = category.find('div', class_='sideBarLeft')
                category_top_li = category_top_div.find_all('li')
                # 一级分类
                category_top = {}
                for top in category_top_li:
                    category_top_span = top.find(
                        'span', class_='sideBarLeftTit')
                    category_top_text = category_top_span.string
                    # 二级分类
                    category_2nd_div = top.find('div', class_='sideBarLinkBox')
                    # 二级分类a节点
                    category_2nd_a = category_2nd_div.find_all('a')
                    # 二级分类
                    category_2nd = {}
                    for a in category_2nd_a:
                        # a节点中href和text
                        category_2nd_href = a.get('href')
                        category_2nd_text = a.string
                        # 添加协议头
                        if category_2nd_href.find(
                                'https') == -1 and category_2nd_href.find(
                                    'http') == -1:
                            category_2nd_href = 'https:' + category_2nd_href
                        category_2nd[category_2nd_text] = category_2nd_href
                    category_top[category_top_text] = category_2nd
                category_industry[category_industry_text] = category_top
        except AttributeError:
            self.logger.error('对象没有这个属性：' + traceback.format_exc())
        except KeyError:
            self.logger.error('映射中没有这个键：' + traceback.format_exc())
        except BaseException:
            self.logger.error('解析分类出错：' + traceback.format_exc())
        return category_industry

    # 解析产品列表
    def interpreting_product_list(self, html_doc):
        try:
            # 存放产品列表
            product_list = []
            doc = BeautifulSoup(html_doc, 'html5lib')
            # 获取产品列表li节点
            product_li = doc.find_all('li', class_='grid-list')
            for li in product_li:
                product = {}

                # 针对部分li节点特殊处理
                li_style = li.get('style', None)
                if li_style and ('display:none' in li_style.replace(' ', '')):
                    continue

                # 获取li节点下img节点产品图片
                product_a = li.find('a', class_='nImgBox')
                if product_a:
                    product_img = product_a.find('img')
                    product_img_src = product_img.get(
                        'data-original') or product_img.get('src')
                    product['img'] = product_img_src
                # 获取li节点下span节点产品价格
                product_span = li.find('span', class_='seaNewPrice')
                if product_span:
                    product_price = product_span.get_text()
                    # product['price'] = product_price
                    if product_price[0] == '¥':
                        product['currency'] = 'CNY'
                        product_price = product_price[1:]
                    if '/' in product_price:
                        price_and_unit = product_price.split('/', 1)
                        # 单位
                        product['unit'] = price_and_unit[1]
                        try:
                            # 价格中存在汉字单位需做相应转换
                            if '万' in price_and_unit[0]:
                                # 去除汉字单位万 换算成10000
                                price_and_unit[0] = price_and_unit[0].rstrip(
                                    '万')
                                # 设置精度为小数点后两位
                                decimal.getcontext().prec = 2
                                price_and_unit[0] = float(
                                    decimal.Decimal(price_and_unit[0])) * 10000
                            elif '亿' in price_and_unit[0]:
                                # 去除汉字单位亿 换算成100000000
                                price_and_unit[0] = price_and_unit[0].rstrip(
                                    '亿')
                                # 设置精度为小数点后两位
                                decimal.getcontext().prec = 2
                                price_and_unit[0] = float(
                                    decimal.Decimal(price_and_unit[
                                        0])) * 100000000
                            product['price'] = price_and_unit[0]
                        except BaseException:
                            self.logger.error('解析产品价格出错：' +
                                              traceback.format_exc())
                            product['price'] = None
                    # 获取li节点下dd节点产品名、产品详情链接
                product_dd = li.find('dd', class_='newName')
                if product_dd:
                    product_info = product_dd.find('a')
                    product['title'] = product_info.get('title')
                    product['href'] = product_info.get('href')
                # 获取li节点下dd节点公司名、公司主页链接
                company_dd = li.find('dd', class_='newCname')
                if company_dd:
                    company_info = company_dd.find('a')
                    product['company'] = company_info.get('title')
                    product['homepage'] = company_info.get('href')
                product_list.append(product)
        except AttributeError:
            traceback.print_exc()
            self.logger.error('对象没有这个属性：' + traceback.format_exc())
        except KeyError:
            self.logger.error('映射中没有这个键：' + traceback.format_exc())
        except BaseException:
            self.logger.error('解析产品列表出错：' + traceback.format_exc())
        return product_list

    # 解析产品详情
    def interpreting_product_details(self, html_doc):
        try:
            # 存储产品信息
            product = {}
            doc = BeautifulSoup(html_doc, 'html5lib')
            # 产品图片
            img = []
            # 产品多图
            product_li = doc.find_all('li', class_='tab-trigger')
            if product_li:
                for li in product_li:
                    product_a = li.find(
                        'a',
                        attrs={
                            "data-useractivelogs":
                            "UserBehavior_detail_smallphoto"
                        })
                    if product_a:
                        # 获取largeimage
                        product_img = product_a.find('img')
                        product_img_src = product_img.get('src')
                        # 获取原图
                        last_index = product_img_src.rfind('..')
                        img.append(product_img_src[:last_index])
            # 该产品不存在多图时，使用默认的一张大图
            else:
                product_img_div = doc.find('div', class_='vertical-img')
                if product_img_div:
                    product_img = product_img_div.find(
                        'a',
                        attrs={
                            "data-useractivelogs":
                            "UserBehavior_detail_bigphoto"
                        })
                    product_img_hrefs = product_img.get('hrefs')
                    if not product_img_hrefs:
                        product_img_src = product_img.find('img').get('src')
                        # 获取原图
                        last_index = product_img_src.rfind('..')
                        product_img_hrefs = product_img_src[:last_index]
                    img.append(product_img_hrefs)
            product['imgs'] = img
            ''' 
            产品详情有两种展示效果，因此需要不同解析
            '''
            # 产品详情整个内容
            pdetail = doc.find(
                'div',
                id='pdetail',
                class_='proDetailCon tab_content_event_class')
            if pdetail is not None:
                # 获取产品唯一识别id
                product_bcid = doc.find('input', id='bcid').get('value')
                detail_bot = pdetail.find('div', class_='detailBot')
                detail_bot.decompose()
                introduce = pdetail.find('div', id='introduce')
                if product_bcid:
                    product['bcid'] = product_bcid
                    xss_filter = 'http://wsdetail.b2b.hc360.com/XssFilter?callback=jQuery&bcid='
                    result_product_introduce = Spider().spider_URL(
                        url=xss_filter + product_bcid)

                    product_introduce = self.interpreting_product_details_desc(
                        result_product_introduce)
                    introduce.replace_with(
                        BeautifulSoup(product_introduce, 'html.parser'))
            else:
                pdetail = doc.find(
                    'div',
                    id='pdetail',
                    class_='pdetail tab_content_event_class')
                if pdetail is not None:
                    # 基本参数
                    vopy = pdetail.find('div', class_="d-vopy")
                    # 去除基本参数列表中图片div
                    vopyImgBoxs = vopy.find_all('div', class_='d-vopyImgBox')
                    for vopyImgBox in vopyImgBoxs:
                        vopyImgBox.decompose()
                    # 去除基本参数列表中同类产品显示span
                    span = pdetail.find_all(
                        'span', class_='same-parameter-commodity-hook')
                    for s in span:
                        s.decompose()
                    # 详细说明div
                    d_xi_b = pdetail.find('div', class_='d-xi-b').find('div')
                    detail_imgs = d_xi_b.find_all('img')
                    if detail_imgs:
                        for img in detail_imgs:
                            del img['onerror']
                            del img['onload']
                    # 详细说明中包含的文本内容(不包含tag标签)
                    content_text = d_xi_b.find_all(text=True, recursive=False)
                    if content_text:
                        for text in content_text:
                            # 全部替换为'' 去除“慧聪网”字眼
                            text.replace_with('')
            style = '''<style>
                            #introduce {font-size: 14px;}
                            table {border-collapse: collapse;border-spacing: 0;}
                            p {margin: 0;}
                            .dvop-title {line-height: 30px;font-size: 14px;color: rgb(51, 51, 51);padding-bottom: 10px;}
                            .dvop-title h4 {font-weight: normal;}
                            .d-vopy table {width: 100%;float: left;font-size: 12px;margin-bottom: 18px;border-left: 1px solid rgb(237, 237, 237);border-top: 1px solid rgb(237, 237, 237);}
                            .d-vopy th {width: 200px;background-color: rgb(245, 245, 245);text-align: center;font-weight: normal;min-height: 34px;line-height: 34px;border-right: 1px solid rgb(237, 237, 237);border-bottom: 1px solid rgb(237, 237, 237);padding: 0px;}
                            .d-vopy td {border-right: 1px solid #ededed;border-bottom: 1px solid #ededed;vertical-align: top;}
                            .d-vopy td {padding-left: 20px;line-height: 34px;}
                            .d-vopy th h4 {font-size: 12px;color: rgb(51, 51, 51);margin: 0px;}
                            .d-vopyList {overflow: hidden;}
                            .d-vopyList {line-height: 34px;padding-left: 20px;}
                            .d-vopyList p {float: left;}
                            .d-vopyList p {padding-right: 20px;width: 500px;line-height: 24px;padding: 5px 0;}
                            .d-xi-b {padding: 10px 0px;font-size: 12px;}
                        </style> '''
            product['details'] = style + pdetail.prettify()
        except AttributeError:
            self.logger.error('对象没有这个属性：' + traceback.format_exc())
        except KeyError:
            self.logger.error('映射中没有这个键：' + traceback.format_exc())
        except BaseException:
            self.logger.error('解析产品详情出错：' + traceback.format_exc())
        return product

    # 解析产品详情中详细说明
    def interpreting_product_details_desc(self, product_introduce):
        introduce = None
        # 解析产品详情页中产品内容详情
        s_index = product_introduce.find('{')
        e_index = product_introduce.rfind('}')
        if s_index != -1 and e_index != -1:
            # 将json转为dict
            result_dict = json.loads(product_introduce[s_index:e_index + 1])
            # 获取html内容
            introduce = result_dict.get('html')
            # ''' 注意：此处不能直接使用
            #     introduce.replace_with(product_introduce)
            #     此做法会导致html无法被转义还原
            # '''
            # introduce.replace_with(
            #     BeautifulSoup(product_introduce, 'html.parser'))
        return introduce

    # 产品详情的拼装
    def assemble_product_details(self, product):

        pass

    # 解析联系方式
    def interpreting_contact_info(self, html_doc):
        try:
            # 存储联系信息
            contacts = {}
            doc = BeautifulSoup(html_doc, 'html5lib')
            # 联系我们div节点
            contacts_div = doc.find('div', class_='leftBox')
            if contacts_div:
                contacts_li = contacts_div.find_all('li')
                for li in contacts_li:
                    li_text = li.get_text()
                    if li_text and ('：' in li_text):
                        li_text_array = li_text.split('：')
                        contacts[li_text_array[0]] = li_text_array[1]
            else:
                contacts_div = doc.find('div', class_='ContacCon3')
                # 此处针对非常规公司联系信息做特殊处理
                if contacts_div:
                    # 联系我们li节点
                    contacts_li = contacts_div.find_all('li')
                    for li in contacts_li:
                        label = li.find('span')
                        if not label:
                            continue
                        # 表头
                        label_name = label.string
                        # 右侧内容
                        right_div = li.find('div', class_='con3Rig')
                        if '联系人' == label_name:
                            linkman_span = right_div.find('span')
                            linkman = linkman_span.get_text()
                            contacts[label_name] = linkman.replace(
                                '\n', '').replace(' ', '').replace('\xa0', '')
                        elif '公司主页' == label_name:
                            homepage_a = right_div.find('a')
                            homepage = homepage_a.get('href')
                            contacts[label_name] = homepage.replace(
                                '\n', '').replace(' ', '')
                        else:
                            other_info = right_div.string
                            contacts[label_name] = other_info.replace(
                                '\n', '').replace(' ', '')
                else:
                    contacts_div = doc.find_all('div', class_='key-message')
                    for div in contacts_div:
                        label = div.find('span')
                        if not label:
                            continue
                        # 表头
                        label_name = label.string
                        # 右侧内容
                        right_em = div.find('em')
                        right_text = right_em.string
                        if right_text and ('：' in right_text):
                            right_text = right_text.string[1:]
                        contacts[label_name] = right_text

        except AttributeError:
            self.logger.error('对象没有这个属性：' + traceback.format_exc())
        except KeyError:
            self.logger.error('映射中没有这个键：' + traceback.format_exc())
        except BaseException:
            self.logger.error('解析联系方式出错：' + traceback.format_exc())
        return contacts
