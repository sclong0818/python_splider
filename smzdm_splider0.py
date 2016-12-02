# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

import string
import urllib2
import re
import json

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
    def __init__(self,url):
        self.myUrl = url
        self.datas = []
        self.myTool = HTML_Tool()
        self.encoding = "utf-8"
        #定义 标签的数据结构
        ##标签 分为 3个层级，用[map]
        ##库 用 parentid 表示
        self.categories = []
        print u'已经启动smzdm商品百科爬虫，咔嚓咔嚓'

    def spider_start(self):
        #读取页面的原始信息并将其从gbk转码
        user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        headers = { 'User-Agent' : user_agent }
        req = urllib2.Request(self.myUrl, headers = headers)
        # myPage = urllib2.urlopen(self.myUrl).read().decode(self.encoding)
        myPage = urllib2.urlopen(req).read().decode(self.encoding)


        # 处理分类
        self.get_categoris(myPage)

        #打印分类，（或者存储分类）
        print json.dumps(self.categories,ensure_ascii=False)

    def get_categoris(self,myPage):
        myMatch = re.search(r'ul id="left-category" class="category_box">(.*?)</ul>',myPage,re.S)
        if myMatch:
            print u'爬虫报告：发现分类信息'
            category_content = myMatch.group(1)
            self.hand_category(category_content)

        else:
            print u'爬虫报告：未发现分类信息'

    def hand_category(self,content):
        myItems = re.findall('<li class.*?>(.*?)</li>',content,re.S)
        print len(myItems)
        for item in myItems:
            parentMatch = re.search(r'h2>.*?<a href=.*?>(.*?)</a>.*?</h2>',item,re.S)
            if parentMatch:
                parentItem = parentMatch.group(1)
                categoryName = self.myTool.Replace_Char(parentItem.replace("\n","").encode(self.encoding))
                subMatch = re.search(r'dl class="sub_category.*?>(.*?)</dl>',item,re.S)
                if subMatch:
                    subItems = subMatch.group(1)
                    subs = self.hand_sub(subItems)
                    category = {}
                    category[categoryName] = subs
                    self.categories.append(category)
                else:
                    print u'爬虫报告：未发现子分类信息'
            else:
                print u'爬虫报告：未发现父分类信息'

    def hand_sub(self,content):
        sub0s = self.hand_sub0(content)
        sub1s = self.hand_sub1(content)
        subs = []
        if len(sub0s) == len(sub1s):
            i = 0
            for sub0 in sub0s:
                sub_dict = {}
                sub_dict[str(sub0)] = sub1s[i]
                i += 1
                subs.append(sub_dict)
        else:
            print u'二级分类及二级分类子内容 长度不匹配'
        return subs


    def hand_sub0(self,content):
        myItems = re.findall('<dt>.*?<a.*?>(.*?)</a>.*?</dt>',content,re.S)
        sub0s = []
        for item in myItems:
            sub0s.append(self.myTool.Replace_Char(item.replace("\n","")))
        return sub0s

    def hand_sub1(self,content):
        myItems = re.findall('<dd>(.*?)</dd>',content,re.S)
        children = []
        for item in myItems:
            sub1s = []
            myChildren = re.findall('<a.*?>(.*?)</a>',item,re.S)
            for child in myChildren:
                sub1s.append(self.myTool.Replace_Char(child.replace("\n","").encode(self.encoding)))
            children.append(sub1s)
        return children

# ---------- 程序入口 --------------
print """#----------------------------
# 程序：smzdm爬虫
# 功能：爬取 smzdm优质商品信息
#----------------------------------------
"""

#wiki 首页
url = 'http://wiki.smzdm.com/youxuan'

mySpider = Smzdm_Spider(url)
mySpider.spider_start()
