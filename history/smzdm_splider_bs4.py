# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

import string
import urllib
import urllib2
import re
import json
from bs4 import BeautifulSoup
import MySQLdb
import os
import httplib


class HTML_Tool:
    # 用 非贪婪模式 匹配 \t 或者\n 或者 空格超链接 和图片
    BgnCharToNoneRex = re.compile("(\t|\n|\r| |<a.*?>|<img.*?>)")

    #用 非贪婪模式 陪 任意 <>
    EndCharToNoneRex = re.compile("<.*?>")

    #用 非贪婪模式匹配 任意 <p> 标签
    BgnPartRex = re.compile("<p.*?>")
    CharToNewLineRex =re.compile("(<br />|</p>|<tr>|<div>|</div>)")
    CharToNewTabRex = re.compile("<td>")

    #将一些html符号尸体转变为原始符号
    replaceTab = [("<","<"),(">",">"),("&","&"),("&","\""),(" "," ")]

    def Replace_Char(self,x):
        x = self.BgnCharToNoneRex.sub("",x)
        x = self.BgnPartRex.sub("\n    ",x)
        x = self.CharToNewLineRex.sub("\n",x)
        x = self.CharToNewTabRex.sub("\t",x)
        x = self.EndCharToNoneRex.sub("",x)

        for t in self.replaceTab:
            x = x.replace(t[0],t[1])
        return x

class Smzdm_Spider:
    #申明相关的属性
    def __init__(self):
        self.categoryUrl = 'http://wiki.smzdm.com/youxuan'
        self.brandUrl = 'http://pinpai.smzdm.com'
        self.mallUrl = 'http://www.smzdm.com/mall'
        self.hide_malls = ['ebay','dell','microsoftstore','newegg','amazon_jp','xiji','sfht','mi'
            ,'amazon_de','joesnewbalanceoutlet','sierratradingpost','amazon_fr','kaola','myhabit','nikestore_cn'
            ,'ehaier','midea','jd_hk','royyoungchemist_cn','amcal_cn','bubugao','supuy'
            ,'muyingzhijia','daling','sasa','amazon_es','6pm','finishline','wiggle','jimmyjazz']
        self.dict_country = {'美国':227,'日本':109,'英国':226,'德国':82,'澳大利亚':13,'西班牙':198,'香港':97,'德国':82,'法国':74}
        self.imgSaveRoot = 'E:\\wiki_img'
        self.datas = []
        self.myTool = HTML_Tool()
        self.encoding = "utf-8"
        print u'已经启动smzdm商品百科爬虫，咔嚓咔嚓'

    def test_print(self):
        print 'hello world'

    def init_db(self):
        print u'数据库连接初始化.....'
        self.conn= MySQLdb.connect(
                host='192.168.0.118',
                port = 3306,
                user='root',
                passwd='root'
                )
        self.conn.select_db('ark1')
        self.conn.set_character_set('utf8')
        self.cur = self.conn.cursor()
        self.cur.execute("SET NAMES utf8;")
        self.cur.execute("SET CHARACTER SET utf8;")
        self.cur.execute("SET character_set_connection=utf8;")
        print u'数据库连接初始化正常.....'

    def close_db(self):
        self.cur.close()
        self.conn.close()
        print u'关闭数据库连接.....'

    def spider_start(self):
        self.init_db()
        #读取页面的原始信息并将其从gbk转码
        user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        headers = { 'User-Agent' : user_agent }
        # 处理分类
        # self.get_categoris(headers)

        # 处理商城
        # self.get_malls(headers)

        # 处理隐藏 mall
        # self.get_malls_hide(headers)

        self.close_db()
        print u'爬虫服务运行结束.....'

    # ------------------------- mall 处理
    def get_malls_hide(self,_headers):
        print u'已经启动隐藏商城爬虫，咔嚓咔嚓'
        #send HTTP/1.0 request , adding this , fix the problem
        httplib.HTTPConnection._http_vsn = 10
        httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'
        malls = []
        category = '综合商城'
        for uri in self.hide_malls:
            url = 'http://www.smzdm.com/mall/'+uri
            detail_req = urllib2.Request(url, headers = _headers)
            detail_page = ''
            mall={}
            mall['uri'] = uri
            try:
                detail_page = urllib2.urlopen(detail_req).read().decode(self.encoding)
            except httplib.IncompleteRead, e:
                detail_page = e.partial
            except Exception as RESTex:
                print("Exception occurred making REST call: " + RESTex.__str__())
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
                    self.saveImg('mall',mall_pic_name,detail['mall_image'])
                    mall['pic_url']='/mall/'+ mall_pic_name

                malls.append(mall)

        #after | back to http 1.1
        httplib.HTTPConnection._http_vsn = 11
        httplib.HTTPConnection._http_vsn_str = 'HTTP/1.1'
        # 去重 & category 处理
        # print json.dumps(malls,ensure_ascii=False)
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
        #i = 0
        for category in mall_categories:
            # i += 1
            # if i>1:
            #     break
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
                except Exception as RESTex:
                    print("Exception occurred making REST call: " + RESTex.__str__())
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
                self.saveImg('mall',mall_pic_name,mall_image)
                mall['pic_url']='/mall/'+ mall_pic_name

                malls.append(mall)

        #after | back to http 1.1
        httplib.HTTPConnection._http_vsn = 11
        httplib.HTTPConnection._http_vsn_str = 'HTTP/1.1'
        # 去重 & category 处理
        #print json.dumps(malls,ensure_ascii=False)
        self.save_malls(malls)
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
        self.insert_malls(sqlvalues)

        # 更新商城的category
        for key in need_updates.keys():
            self.update_mall_categories((str(need_updates[key]),key))

        self.conn.commit()

    def update_mall_categories(self,sqlvalues):
        self.cur.execute('update mall set categories=%s where name=%s',sqlvalues)

    def insert_malls(self,sqlvalues):
        self.cur.executemany('insert into mall(name,categories,uri,excerpt,summary,recommend,pic_url,url,country_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',sqlvalues)

    def createFile(self,save_path,filename):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_path = os.path.join(save_path, filename)
        if not os.path.exists(file_path):
            file = open(file_path,'a+')
            file.close()
            return file_path
        else:
            # 已存在同名文件
            return ''

    def saveImg(self,subpath,filename,imgurl):
        save_path = os.path.join(self.imgSaveRoot,subpath)
        file_path = self.createFile(save_path,filename)
        if file_path:
            urllib.urlretrieve(imgurl,file_path,None)

    # ------------------------- category 处理
    def get_categoris(self,_headers):
        req = urllib2.Request(self.categoryUrl, headers = _headers)
        myPage = urllib2.urlopen(req).read().decode(self.encoding)
        soup = BeautifulSoup(myPage,'lxml')

        li_list = soup.select('ul[id="left-category"] > li')
        # {name:name,parent_id:parent_id,level:level,uri:uri}
        for item in li_list:
            # 查找一级分类 li div[class=li_item] > h2 > a
            node_1 = item.select('div[class="li_item"] > h2 > a')
            if node_1:
                #print node_1[0].contents[0].string
                #print node_1[0].get_text()
                category = self.hand_category_a(node_1[0])
                category['parent_id'] = -1
                category['level'] = 0
                self.insert_category(category)
                category['id'] = self.conn.insert_id()
                print json.dumps(category,ensure_ascii=False)

                # 处理 2 级 和 3级 类别
                dl_dt_a = item.select('dl[class="sub_category"] > dt > a')
                dl_dd = item.select('dl[class="sub_category"] > dd')
                sub_for_index = 0
                if len(dl_dt_a) == len(dl_dd):
                    for sub_2 in dl_dt_a:
                        subcate_2 = self.hand_category_a(sub_2)
                        subcate_2['parent_id'] = category['id']
                        subcate_2['level'] = 1
                        self.insert_category(subcate_2)
                        subcate_2['id'] = self.conn.insert_id()
                        print "   "+json.dumps(subcate_2,ensure_ascii=False)
                        # 三级类别
                        dl_dd_a = dl_dd[sub_for_index].find_all('a')
                        sub_for_index +=1
                        for sub_3 in dl_dd_a:
                            subcate_3 = self.hand_category_a(sub_3)
                            subcate_3['parent_id'] = subcate_2['id']
                            subcate_3['level'] = 2
                            self.insert_category(subcate_3)
                            subcate_3['id'] = self.conn.insert_id()
                            print "      "+json.dumps(subcate_3,ensure_ascii=False)
                # 记得提交
                self.conn.commit()

    def hand_category_a(self,a):
        category = {}
        category['name'] =  self.myTool.Replace_Char(a.get_text().replace("\n","").encode(self.encoding))
        href =a['href']
        pos = href[0:len(href)-1].rfind('/')
        category['uri'] = href[:pos]
        return category

    def insert_category(self,category):
        self.cur.execute('insert into category(name,parent_id,level,uri) values(%s,%s,%s,%s)',[category['name'],category['parent_id'],category['level'],category['uri']])

# ---------- 程序入口 --------------
print """#----------------------------
# 程序：smzdm爬虫
# 功能：爬取 smzdm优质商品信息
#----------------------------------------
"""

mySpider = Smzdm_Spider()
#mySpider.spider_start()
