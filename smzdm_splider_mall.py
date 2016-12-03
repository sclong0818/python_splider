# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

import string
import urllib
import urllib2
import json
from bs4 import BeautifulSoup
import httplib

from html_tool import HTML_Tool
from smzdm_mysql import SMZDM_Mysql
from file_tool import File_Tool

class Mall_Spider:
    #申明相关的属性
    def __init__(self):
        self.encoding = "utf-8"
        self.mallUrl = 'http://www.smzdm.com/mall'
        self.hide_malls = ['ebay','dell','microsoftstore','newegg','amazon_jp','xiji','sfht','mi'
            ,'amazon_de','joesnewbalanceoutlet','sierratradingpost','amazon_fr','kaola','myhabit','nikestore_cn'
            ,'ehaier','midea','jd_hk','royyoungchemist_cn','amcal_cn','bubugao','supuy'
            ,'muyingzhijia','daling','sasa','amazon_es','6pm','finishline','wiggle','jimmyjazz']
        self.dict_country = {'美国':227,'日本':109,'英国':226,'德国':82,'澳大利亚':13,'西班牙':198,'香港':97,'德国':82,'法国':74}
        self.imgSaveRoot = 'E:\\wiki_img'
        self.file_tool = File_Tool()
        self.db = SMZDM_Mysql()
        self.myTool = HTML_Tool()

    def test_print(self):
        print 'hello world'

    def spider_start(self):
        print u'已经启动Mall 爬虫，咔嚓咔嚓'
        self.db.init_db()

        user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        headers = { 'User-Agent' : user_agent }
        try:
            # 处理商城
            self.get_malls(headers)

            # 处理隐藏 mall
            self.get_malls_hide(headers)
        except Exception as ex:
            self.db.close_db()
            print("Exception occurred get_malls | get_malls_hide call: " + ex.__str__())
            return ''

        self.db.close_db()
        print u'Mall 爬虫服务运行结束.....'

    # ------------------------- mall 处理
    def get_malls_hide(self,_headers):
        print u'已经启动隐藏商城爬虫，咔嚓咔嚓'
        #send HTTP/1.0 request , adding this , fix the problem
        httplib.HTTPConnection._http_vsn = 10
        httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'
        malls = []
        category = '综合商城'
        for uri in self.hide_malls:
            url = self.mallUrl +'/'+ uri
            detail_req = urllib2.Request(url, headers = _headers)
            detail_page = ''
            mall={}
            mall['uri'] = uri
            try:
                detail_page = urllib2.urlopen(detail_req).read().decode(self.encoding)
            except httplib.IncompleteRead, e:
                detail_page = e.partial
            except Exception as RESTex:
                print("Exception occurred get mall detail page call: " + RESTex.__str__())
                continue
            detail = self.get_mall_details(detail_page)
            if detail:
                mall['name'] = detail['name']
                mall['url'] = detail['url']
                mall['country'] = detail['country']
                mall['excerpt'] = detail['excerpt']
                mall_image = detail['mall_image']
                mall['category'] = category
                mall['recommend'] = 5
                mall['summary'] = ''
                # save image to local
                if detail['mall_image']:
                    origin_image = detail['mall_image'].replace('_g320.jpg','')
                    pos = origin_image.rfind('/')
                    mall_pic_name = origin_image[pos+1:]
                    self.file_tool.saveImg(self.imgSaveRoot,'mall',mall_pic_name,detail['mall_image'])
                    mall['pic_url']='/mall/'+ mall_pic_name

                malls.append(mall)

        #after | back to http 1.1
        httplib.HTTPConnection._http_vsn = 11
        httplib.HTTPConnection._http_vsn_str = 'HTTP/1.1'
        # 去重 & category 处理
        print json.dumps(malls,ensure_ascii=False)
        self.save_malls(malls)
        print u'隐藏商城爬虫已经结束，咔嚓咔嚓......'

    def get_malls(self,_headers):
        print u'已经启动商城爬虫，咔嚓咔嚓'
        #send HTTP/1.0 request , adding this , fix the problem
        httplib.HTTPConnection._http_vsn = 10
        httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

        req = urllib2.Request(self.mallUrl, headers = _headers)
        myPage = urllib2.urlopen(req).read().decode(self.encoding)
        soup = BeautifulSoup(myPage,'lxml')
        malls = []
        recommend_char='★'
        mall_categories = soup.find_all('div',class_="category")
        for category in mall_categories:
            dom_cate_name = category.find('div',class_='sc-title')
            cate_name = self.myTool.Replace_Char(dom_cate_name.get_text().replace("\n","").encode(self.encoding))
            #print cate_name
            mall_lis = category.select('div[class="sc-container"] > ul > li')
            for mall_li in mall_lis:
                mall = {}
                mall['category'] = cate_name
                dom_mall_name_a = mall_li.select('div[class="sc-show-title"] > a')
                mall['name'] = dom_mall_name_a[0].get_text()
                #print mall['name']
                dom_mall_summary = mall_li.find('div',class_='sc-show-info')
                mall['summary'] = self.myTool.Replace_Char(dom_mall_summary.get_text().replace("\n","").encode(self.encoding))

                dom_mall_recommend_span = mall_li.find('span')
                mall['recommend']= dom_mall_recommend_span.get_text().count(recommend_char)

                mall_image = mall_li.find('img')["src"]
                # 跳转到商城详情
                detail_url = mall_li.find('a',class_='sc-detail')['href']
                pos_ = detail_url[0:len(detail_url)-1].rfind('/')
                mall['uri'] = detail_url[:pos_]
                detail_req = urllib2.Request(detail_url, headers = _headers)
                detail_page = ''
                try:
                    detail_page = urllib2.urlopen(detail_req).read().decode(self.encoding)
                except httplib.IncompleteRead, e:
                    detail_page = e.partial
                except Exception as ex:
                    print("Exception occurred get mall detail page call: " + ex.__str__())
                    continue
                detail = self.get_mall_details(detail_page)
                if detail:
                    mall['url'] = detail['url']
                    mall['country'] = detail['country']
                    mall['excerpt'] = detail['excerpt']
                    mall_image = detail['mall_image']

                # save image to local
                origin_image = mall_image.replace('_g320.jpg','')
                pos = origin_image.rfind('/')
                mall_pic_name = origin_image[pos+1:]
                self.file_tool.saveImg(self.imgSaveRoot,'mall',mall_pic_name,mall_image)
                mall['pic_url']='/mall/'+ mall_pic_name

                malls.append(mall)

        #after | back to http 1.1
        httplib.HTTPConnection._http_vsn = 11
        httplib.HTTPConnection._http_vsn_str = 'HTTP/1.1'
        # 去重 & category 处理
        print json.dumps(malls,ensure_ascii=False)
        #self.save_malls(malls)
        print u'商城爬虫已经结束，咔嚓咔嚓......'

    def get_mall_details(self,detail_page):
        detail = {}
        soup_detail = BeautifulSoup(detail_page,'lxml')
        dom_detail_info_div = soup_detail.find('div',class_='sjdhInfoBox')
        if dom_detail_info_div:
            #name
            dom_mall_name_h1 = dom_detail_info_div.find('h1',class_='fontTitle')
            if dom_mall_name_h1:
                detail['name'] = dom_mall_name_h1.get_text()
            # 图片处理
            dom_detail_img_a = dom_detail_info_div.select('div[class="sjdhPic"] > a > img')
            detail_img_a = dom_detail_img_a[0]
            if detail_img_a:
                detail['mall_image'] = detail_img_a['src']
            # url
            mall_url_a_attr_ = {'rel':'nofollow','class':'blue'}
            dom_mall_url_a = dom_detail_info_div.find('a',mall_url_a_attr_)
            detail['url'] = dom_mall_url_a.get_text() if dom_mall_url_a else ''
            dom_mall_country_span = dom_detail_info_div.select('div[class="mallAddress"] > span')
            if dom_mall_country_span[0]:
                detail['country'] = dom_mall_country_span[0].get_text()
            dom_mall_excerpt_p = dom_detail_info_div.find('p',class_='p_excerpt')
            if dom_mall_excerpt_p:
                detail['excerpt'] = self.myTool.Replace_Char(dom_mall_excerpt_p.get_text().replace("\n","").encode(self.encoding))
        return detail

    def save_malls(self,malls):
        sqlvalues = []
        mall_name_set =set([])
        mall_name_cate_map = {}
        need_updates = {}
        for mall in malls:
            key = mall['name']
            #重复处理
            if key in mall_name_set:
                if key in mall_name_cate_map:
                    cate_old = mall_name_cate_map.get(key)
                    if mall['category'] != cate_old:
                        mall_name_cate_map[key] = cate_old+','+mall['category']
                        need_updates[key] = mall_name_cate_map[key]
            else:
                mall_name_set.add(key)
                #地域处理
                country_id = 44
                ctry = str(mall['country'])
                if ctry in self.dict_country:
                    country_id = self.dict_country[ctry]

                mall_name_cate_map[key] = '综合电商'
                if mall['category']:
                    mall_name_cate_map[key] = mall['category']
                sqlvalues.append((mall['name'],mall_name_cate_map[key],mall['uri'],mall['excerpt'],mall['summary'],mall['recommend'],mall['pic_url'],mall['url'],country_id))

        # 批量插入 商城
        #print sqlvalues
        self.db.insert_malls(sqlvalues)

        # 更新商城的category
        for key in need_updates.keys():
            self.db.update_mall_categories((str(need_updates[key]),key))

        self.db.commit()
