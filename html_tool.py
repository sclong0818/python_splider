# -*- coding: utf-8 -*-
import re

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

    def test_print(self):
        print 'hello html tools'

    def Replace_Char(self,x):
        x = self.BgnCharToNoneRex.sub("",x)
        x = self.BgnPartRex.sub("\n    ",x)
        x = self.CharToNewLineRex.sub("\n",x)
        x = self.CharToNewTabRex.sub("\t",x)
        x = self.EndCharToNoneRex.sub("",x)

        for t in self.replaceTab:
            x = x.replace(t[0],t[1])
        return x

html_tool = HTML_Tool()
