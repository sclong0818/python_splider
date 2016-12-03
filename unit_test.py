# -*- coding: utf-8 -*-
import string
import urllib2
import json
from bs4 import BeautifulSoup
import httplib

from sys import path
path.append(r'H:\code\python')

from smzdm_splider_category import Categories_Spider
from smzdm_splider_mall import Mall_Spider

c_spider = Categories_Spider()
c_spider.test_print()

m_spider = Mall_Spider()
m_spider.test_print()
