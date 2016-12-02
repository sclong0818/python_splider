# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

import string
import urllib
import urllib2
import json
from bs4 import BeautifulSoup

from html_tool import HTML_Tool
from smzdm_mysql import SMZDM_Mysql

class Categories_Spider:
    #申明相关的属性
    def __init__(self):
        self.encoding = "utf-8"
        self.categoryUrl = 'http://wiki.smzdm.com/youxuan'
        self.myTool = HTML_Tool()
        self.db = SMZDM_Mysql()

    def test_print(self):
        print 'hello world'

    def spider_start(self):
        print u'已经启动Categories 爬虫，咔嚓咔嚓'
        self.db.init_db()
        #读取页面的原始信息并将其从gbk转码
        user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        headers = { 'User-Agent' : user_agent }
        # 处理分类
        try:
            self.get_categoris(headers)
        except Exception as ex:
            self.db.close_db()
            print("Exception occurred get_categoris call: " + ex.__str__())
            return ''

        self.db.close_db()
        print u'Categories 爬虫服务运行结束.....'

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
                self.db.insert_category(category)
                category['id'] = self.db.get_conn().insert_id()
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
                        self.db.insert_category(subcate_2)
                        subcate_2['id'] = self.db.get_conn().insert_id()
                        print "   "+json.dumps(subcate_2,ensure_ascii=False)
                        # 三级类别
                        dl_dd_a = dl_dd[sub_for_index].find_all('a')
                        sub_for_index +=1
                        for sub_3 in dl_dd_a:
                            subcate_3 = self.hand_category_a(sub_3)
                            subcate_3['parent_id'] = subcate_2['id']
                            subcate_3['level'] = 2
                            self.db.insert_category(subcate_3)
                            subcate_3['id'] = self.db.get_conn().insert_id()
                            print "      "+json.dumps(subcate_3,ensure_ascii=False)
                # 记得提交
                self.db.conn.commit()

    def hand_category_a(self,a):
        category = {}
        category['name'] =  self.myTool.Replace_Char(a.get_text().replace("\n","").encode(self.encoding))
        href =a['href']
        pos = href[0:len(href)-1].rfind('/')
        category['uri'] = href[1:pos]
        return category
