# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
html_doc = '<html><head><title>The Dormouse s story</title></head><div class="title"><b>The Dormouse s story</div></p><p id="xxx" class="story">Once upon a time there were three little sisters; and their names were<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;and they lived at the bottom of a well.</p><p class="story">...</p>'
# html_doc = open('test-Zhilian-list-page-sm1.html', 'r').read().decode('utf-8')
soup = BeautifulSoup(html_doc,'lxml')
# print(soup.prettify())
print soup.title
print soup.title.name
print soup.title.string

print soup.p

print "---------------"
print soup.p["class"]

print soup.find_all('a')

x = soup.find_all('a')

for item in x:
    print item

print "---------------"

print soup.find_all(id='newlist')

print soup.find_all('p',class_='story')

attr_ = {'class':'story','id':'xxxx'}
print soup.find_all('p',attr_)

print soup.select('div[class*=title]')
print "---------------"

print soup.find_all(align="center")
# soup_2 = BeautifulSoup(soup.find_all('p',p_attrs,False),'lxml')
# print(soup_2.prettify())

print '---------------------'
print soup.find_all(attrs={'id':re.compile("para$")})
