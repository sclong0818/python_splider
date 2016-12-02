# -*- coding=utf-8 -*-#
# 一个简单的re实例，匹配字符串中的hello字符串

import re

pattern = re.compile(r'hello')

match1 = pattern.match('hello world!')
match2 = pattern.match('helloo world!')
match3 = pattern.match('helllo world!')

if match1:
    print match1.group()
else:
    print 'match1 匹配失败'

if match2:
    print match2.group()
else:
    print 'match2 匹配失败'

if match3:
    print match3.group()
else:
    print 'match3 匹配失败'
