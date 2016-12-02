# -*- coding:utf-8 -*- #
import string,urllib2

print 'hello'

def baidu_tieba(url,begin_page,end_page):
    for i in range(begin_page,end_page+1):
        sName = string.zfill(i,5)+'.html'
        print 'print '+str(i)+u'th page,and save as '+sName+'.....'
        f = open(sName,'w+')
        m = urllib2.urlopen(url+str(i)).read()
        f.write(m)
        f.close()

bdurl = 'http://tieba.baidu.com/p/4866905318'
iPostBegin = 1
iPostEnd = 2

#bdurl = str(raw_input(u'请输入贴吧的地址，去掉pn=后面的数字：\n'))
#iPostBegin = int(raw_input(u'请输入开始的页数：\n'))
#iPostEnd = int(raw_input(u'请输入终点的页数：\n'))

baidu_tieba(bdurl,iPostBegin,iPostEnd)
