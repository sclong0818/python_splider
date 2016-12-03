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

class Tag_Spider:
    #申明相关的属性
    def __init__(self):
        self.encoding = "utf-8"
        self.homeUrl = 'http://wiki.smzdm.com/youxuan/'
        self.tagUrl = 'http://wiki.smzdm.com/t'
        self.db = SMZDM_Mysql()
        self.myTool = HTML_Tool()

        self.old_tags = {}

    def test_print(self):
        print 'hello world'

    def get_tags_hot(self):
        list_tag =self.db.get_tags()
        for tag in list_tag:
            self.old_tags[tag[1]] = tag[0]

    def spider_start(self):
        print u'已经启动Tag 爬虫，咔嚓咔嚓'
        self.db.init_db()
        self.get_tags_hot()
        user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        headers = { 'User-Agent' : user_agent }
        try:
            #send HTTP/1.0 request , adding this , fix the problem
            httplib.HTTPConnection._http_vsn = 10
            httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'
            # 处理热门标签
            #self.splider_hot_tags(headers)

            # 处理一般标签，轮询url
            self.splider_all_tags(headers)

            #after | back to http 1.1
            httplib.HTTPConnection._http_vsn = 11
            httplib.HTTPConnection._http_vsn_str = 'HTTP/1.1'
        except Exception, e:
            self.db.close_db()
            print Exception,":",e
            return ''

        self.db.close_db()
        print u'Tag 爬虫服务运行结束.....'

    def splider_all_tags(self,_headers):
        print u'已经启动get_tags....'
        _x_200 = range(1,200)

        tags = []
        for x in _x_200:
            t_url = self.tagUrl + str(x)
            print t_url
            try:
                req = urllib2.Request(t_url, headers = _headers)
                myPage = urllib2.urlopen(req).read().decode(self.encoding)
                soup = BeautifulSoup(myPage,'lxml')

                dom_tag_a = soup.select('div[class*="right_wrap"] > div[class*="right_top_title"] > div[class*="lFloat"] > a')
                if not dom_tag_a:
                    continue
                tag ={'hot':0,'hot_tag':0}
                tag['name'] = self.myTool.Replace_Char(dom_tag_a[0].get_text().replace("\n","").encode(self.encoding))
                if tag['name'] in self.old_tags:
                    print u'该tag 已经处理过'
                    continue

                dom_tag_hotnumb_div = soup.select('div[class*="right_wrap"] > div[class*="right_top_title"] > div[class="total_pro"]')
                if dom_tag_hotnumb_div:
                    hot_numb_text = dom_tag_hotnumb_div[0].get_text()
                    print hot_numb_text
                    tag['hot_tag'] = int(hot_numb_text.replace('共','').replace('条产品',''))

                if tag['hot_tag'] == 0:
                    continue
                print(u'增加" %s "tag'%tag['name'])
                tags.append(tag)
            except:
                print u'当前page 没有tag 存在'
                continue

            # 按照类别 分批入库
        #print json.dumps(tags,ensure_ascii=False)
        self.save_tags(tags)

    def splider_hot_tags(self,_headers):
        print u'已经启动get_tags....'
        req = urllib2.Request(self.homeUrl, headers = _headers)
        myPage = urllib2.urlopen(req).read().decode(self.encoding)
        soup = BeautifulSoup(myPage,'lxml')
        tags = []
        dom_tags_a = soup.select('div[class="hot_tags_box"] > div[class="tags"] > a')
        for tag_a in dom_tags_a:
            tag = {}
            tag['name'] = tag_a.get_text().replace(' ','')
            tag['hot_tag']= 1
            tag['hot']= 1
            tags.append(tag)

            # 按照类别 分批入库
        self.save_tags(tags)

    def save_tags(self,tags):
        if not tags:
            return ''
        sqlvalues = []
        for bean in tags:
            sqlvalues.append((bean['name'],bean['hot_tag'],bean['hot']))

        # 批量插入 商城
        #print sqlvalues
        self.db.insert_tags(sqlvalues)
        self.db.commit()
