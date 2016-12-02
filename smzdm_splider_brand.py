# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

import string
import urllib2
import json
from bs4 import BeautifulSoup
import httplib

from html_tool import HTML_Tool
from smzdm_mysql import SMZDM_Mysql
from file_tool import File_Tool

class Brand_Spider:
    #申明相关的属性
    def __init__(self):
        self.encoding = "utf-8"
        self.homeUrl = 'http://pinpai.smzdm.com/'
        self.imgSaveRoot = 'E:\\wiki_img'
        self.file_tool = File_Tool()
        self.db = SMZDM_Mysql()
        self.myTool = HTML_Tool()

        self.countries = {}
        self.categories = {}

    def test_print(self):
        print 'hello world'

    def prepare_countries(self):
        _countries = self.db.get_country()
        for country in _countries:
            self.countries[country[2]] = country[0]

    def prepare_categories(self):
        _categories = self.db.get_big_categories()
        for category in _categories:
            self.categories[category[2]] = category[0]

    def spider_start(self):
        print u'已经启动Brand 爬虫，咔嚓咔嚓'
        self.db.init_db()
        # 准备工作
        self.prepare_countries()
        self.prepare_categories()

        # 处理逻辑
        # 1. 按照 category 的uri 请求网页，解析品牌个数 & 品牌第一页
        # 2. 如果品牌数>1000 则 请求品牌第二页。后面的品牌全部忽略
        # 3. 品牌 需要进入品牌详情页，读取品牌描述和品牌地区
        # 4. 保存品牌图片 ，品牌信息入库

        user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        headers = { 'User-Agent' : user_agent }
        try:
            # 处理商城
            self.get_brands(headers)
        except Exception as ex:
            self.db.close_db()
            print("Exception occurred get_brand call: " + ex.__str__())
            return ''

        self.db.close_db()
        print u'Brand 爬虫服务运行结束.....'

    def get_brands(self,_headers):
        print u'已经启动get_brands....'
        i = 0
        for cate_uri in self.categories:
            # i +=1
            # if i>2:
            #     break
            brand_cate_url = self.homeUrl + cate_uri
            #send HTTP/1.0 request , adding this , fix the problem
            httplib.HTTPConnection._http_vsn = 10
            httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

            req = urllib2.Request(brand_cate_url, headers = _headers)
            myPage = urllib2.urlopen(req).read().decode(self.encoding)
            soup = BeautifulSoup(myPage,'lxml')

            splide_page = 1
            dom_brand_cate_numbs_span = soup.select('div[class="brand-classify"] > ul > li > a[class="selected"] > span')
            if dom_brand_cate_numbs_span[0]:
                numbs_str = dom_brand_cate_numbs_span[0].get_text()
                if numbs_str:
                    numbs = numbs_str.replace('（','').replace('）','')
                    splide_page = int(numbs)/1000 + 1
                    splide_page = 3 if splide_page>=3 else splide_page

            brands =[]
            # 获取当前页面的所有品牌
            dom_brands_li = soup.select('ul[class*="brands"] > li')

            # 如果需要抓取第二页
            if splide_page == 2:
                req2 = urllib2.Request(brand_cate_url+'/p2', headers = _headers)
                myPage2 = urllib2.urlopen(req2).read().decode(self.encoding)
                soup2 = BeautifulSoup(myPage2,'lxml')
                dom_brands_li_page2 = soup2.select('ul[class*="brands"] > li')
                dom_brands_li = dom_brands_li + dom_brands_li_page2

            if splide_page == 3:
                req3 = urllib2.Request(brand_cate_url+'/p3', headers = _headers)
                myPage3 = urllib2.urlopen(req3).read().decode(self.encoding)
                soup3 = BeautifulSoup(myPage3,'lxml')
                dom_brands_li_page3 = soup3.select('ul[class*="brands"] > li')
                dom_brands_li = dom_brands_li + dom_brands_li_page3

            print("%s需要爬取%d页数,共计%d个品牌"%(cate_uri,splide_page,len(dom_brands_li)))

            j = 0
            for brand_li in dom_brands_li:
                # if j>10:
                #     break
                # j +=1
                brand = {}
                brand['category'] = self.categories[cate_uri]
                detail_brand_a = brand_li.find('a')
                brand_detail_url = detail_brand_a['href']

                dom_brand_name_div = brand_li.find('div',class_='brands-name')
                if dom_brand_name_div:
                    brand['name'] = self.myTool.Replace_Char(dom_brand_name_div.get_text().replace("\n","").encode(self.encoding))
                    if not brand['name']:
                        continue

                # 图片处理
                dom_brand_img = brand_li.find('img')
                if dom_brand_img:
                    brand_image = dom_brand_img['src']
                    # save image to local
                    origin_image = brand_image.replace('_d200.jpg','')
                    pos = origin_image.rfind('/')
                    brand_pic_name = origin_image[pos+1:]
                    self.file_tool.saveImg(self.imgSaveRoot,'brand',brand_pic_name,brand_image)
                    brand['pic_url']='/brand/'+ brand_pic_name

                # 进入详情页处理
                detail_req = urllib2.Request(brand_detail_url, headers = _headers)
                detail_page = ''
                try:
                    detail_page = urllib2.urlopen(detail_req).read().decode(self.encoding)
                except httplib.IncompleteRead, e:
                    print("Exception occurred httplib.IncompleteRead")
                    detail_page = e.partial
                except Exception as ex:
                    print("Exception occurred get brand detail page call: " + ex.__str__())
                    continue
                if detail_page:
                    detail = self.get_brand_detail(detail_page)
                    if detail:
                        brand['hot_tag'] = detail['hot_tag']
                        brand['country'] = detail['country']
                        brand['desc'] = detail['desc']

                brands.append(brand)
            # 按照类别 分批入库
            self.save_brands(brands)

    def get_brand_detail(self,detail_page):
        detail = {}
        soup_detail = BeautifulSoup(detail_page,'lxml')
        # hot_tag 处理
        # 注意： 该dom标签无法明示，后面可以改为 兄弟dom搜索模式
        dom_hot_tag_div = soup_detail.select('ul[class*="brand-tab"] > a > li > div[class*="brand-tab-title"]')
        if dom_hot_tag_div[0]:
            numbs_str = dom_hot_tag_div[0].get_text()
            if numbs_str:
                numbs = numbs_str.replace('优惠（','').replace('）','')
                detail['hot_tag'] = int(numbs)

        # 地域处理
        dom_brand_country_a = soup_detail.select('div[class*="brand-detail"] > div[class*="brand-country"] > a')
        if dom_brand_country_a[0]:
            country_str = dom_brand_country_a[0].get_text()
            detail['country'] = self.get_country_id(country_str)

        # desc 处理
        dom_brand_desc_div = soup_detail.select('div[class*="brand-info-detail"] > div[class*="pop-content"]')
        if dom_brand_desc_div[0]:
            desc_str = dom_brand_desc_div[0].get_text()
            detail['desc'] = self.myTool.Replace_Char(desc_str.replace("\n","").encode(self.encoding))
        return detail

    def get_country_id(self,name):
        country_id = 44
        ctry = str(name)
        if ctry in self.countries:
            country_id = self.countries[ctry]
        return country_id


    def save_brands(self,brands):
        sqlvalues = []
        for bean in brands:
            sqlvalues.append((bean['name'],bean['desc'],bean['pic_url'],bean['country'],bean['category'],bean['hot_tag']))

        # 批量插入 商城
        #print sqlvalues
        self.db.insert_brands(sqlvalues)

        self.db.commit()

b_splider = Brand_Spider()
b_splider.spider_start()
