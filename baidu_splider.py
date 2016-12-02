# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
import string
import urllib2
import re

class HTML_Tool:
    # 用 非贪婪模式 匹配 \t 或者\n 或者 空格超链接 和图片
    BgnCharToNoneRex = re.compile("(\t|\n| |<a.*?>|<img.*?>)")

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

class Baidu_Spider:
    #申明相关的属性
    def __init__(self,url):
        self.myUrl = url + '?see_lz=1'
        self.datas = []
        self.myTool = HTML_Tool()
        self.encoding = "utf-8"
        print u'已经启动百度贴吧爬虫，咔嚓咔嚓'

    def baidu_tieba(self):
        #读取页面的原始信息并将其从gbk转码
        myPage = urllib2.urlopen(self.myUrl).read().decode(self.encoding)
        #计算楼主发布内容一共有多少页
        endPage= self.page_counter(myPage)
        #获取该帖的标题
        title = self.find_title(myPage)
        #获取最终数据
        self.save_data(self.myUrl,title,endPage)

    #用来计算一共多少页面
    def page_counter(self,myPage):
        myMatch = re.search(r'class="red">(\d+?)</span>',myPage,re.S)
        if myMatch:
            endPage = int(myMatch.group(1))
            print u'爬虫报告：发现楼主共有%d页的原创内容' % endPage
        else:
            endPage = 0
            print u'爬虫报告：无法计算楼主发布内容有多少页'
        return endPage

    def find_title(self,myPage):
        # 匹配 <h1 class="core_title_txt" title="">xxxx<h1> 找出标题
        myMatch = re.search(r'<h3 class="core_title_txt.*?>(.*?)</h3>',myPage,re.S)
        title = u'暂无标题'
        if myMatch:
            title = myMatch.group(1)
        else:
            print u'爬虫报告：无法加载文章标题'
        # 文件名不能包含以下文字
        title = title.replace('\\','').replace('/','').replace(':','').replace('*','')
        title = title.replace('?','').replace('"','').replace('>','').replace('<','').replace('|','')
        return title

    # 用来存储楼主发布的内容
    def save_data(self,url,title,endPage):
        #加载页面数据到数组
        self.get_data(url,endPage)
        #打开本地文件
        f = open(title+ '.txt','w+')
        f.writelines(self.datas)
        f.close()
        print u'爬虫报告：文件已经下载到本地文件并打包成txt文件'
        print u'按任意键退出......'
        #raw_input();

    def get_data(self,url,endPage):
        url = url + '&pn='
        for i in range(1,endPage+1):
            print u'爬虫报告：爬虫%d号正在加载中...' % i
            myPage = urllib2.urlopen(url+ str(i)).read()
            #将myPage中的html代码处理并存储到datas里面
            self.deal_data(myPage.decode(self.encoding))

    #将页面内容从页面代码中抠出来
    def deal_data(self,myPage):
        #myItems= re.findall('id="post_content.*?>(.*?)</div>',myPage,re.S)
        myItems= re.findall('class="post_bubble_middle.*?>(.*?)</div>',myPage,re.S)
        for item in myItems:
            data = self.myTool.Replace_Char(item.replace("\n","").encode(self.encoding))
            self.datas.append(data+"\n")


# ---------- 程序入口 --------------
print """#----------------------------
# 程序：百度贴吧爬虫
# 功能：将楼主发布的内容打包成txt存储到本地
#----------------------------------------
"""

#以某小说贴吧为例
bdurl = 'http://tieba.baidu.com/p/4778938584?see_lz=1&pn=1'

print '请输入贴吧的地址最后的数字串：'
#bdurl = 'http://tieba.baidu.com/p/' + str(raw_input(u'http://tieba.baidu.com/p/'))

mySpider = Baidu_Spider(bdurl)
mySpider.baidu_tieba()
