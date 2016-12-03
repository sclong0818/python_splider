# -*- coding: utf-8 -*-

from smzdm_splider_category import Categories_Spider
from smzdm_splider_mall import Mall_Spider
from smzdm_splider_brand import Brand_Spider
from smzdm_splider_tag import Tag_Spider

class Smzdm_Spider:
    def start(self):
        print u'---------------------------------'
        # 启动 categories 爬虫
        #c_spider = Categories_Spider()
        #c_spider.spider_start()

        # 启动 mall 爬虫
        #m_spider = Mall_Spider()
        #m_spider.test_print()
        #m_spider.spider_start()

        # 启动 mall 爬虫
        #b_spider = Brand_Spider()
        #b_spider.test_print()
        # b_spider.spider_start()

        # 启动 tag 爬虫
        t_spider = Tag_Spider()
        t_spider.test_print()
        #t_spider.spider_start()

# ---------- 程序入口 --------------
print """#----------------------------
# 程序：smzdm爬虫
# 功能：爬取 smzdm优质商品及附属信息
#----------------------------------------
"""

mySpider = Smzdm_Spider()
mySpider.start()
