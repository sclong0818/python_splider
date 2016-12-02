# Python 操作记录

## 基本环境

安装 setuptools

	python ez_setup.py


## Python & Mysql

### 安装MySQL-python

要想使python可以操作mysql 就需要MySQL-python驱动，它是python 操作mysql必不可少的模块。

下载地址：https://pypi.python.org/pypi/MySQL-python/

下载MySQL-python-1.2.5.zip 文件之后直接解压。进入MySQL-python-1.2.5目录:

	>>python setup.py install

测试是否安装成功：

	python
	import MySQLdb


## python  bs4 包

安装相关依赖

	pip install wheel
	easy_install lxml
	//pip install lxml-3.6.4-cp27-cp27m-win32.whl

	# 安装html5lib
	# 关于bs4的文档解析器 ##############
    # 又是一个大坑：bs升级到4后，实例化时需要明确指定文档解析器，如：
    # soup = BeautifulSoup(html_doc, 'lxml')
    # 但是著名的lxml在这里就是个大坑啊，
    # 因为它会直接略过html所有没写规范的tag，而不管人家多在乎那些信息
    # 因为这个解析器的事，我少说也折腾了好几个小时才找到原因吧。
    # 总结：记住，选择html5lib！效率没查多少，最起码容错率强，不会乱删你东西！


安装

	easy_install beautifulsoup4

相关教程

	http://www.jianshu.com/p/55fc16eebea4
	https://my.oschina.net/guol/blog/95947

## Python & Splider

** 往mysql 批量插入 含中文的记录时，报下面的错误： **

		UnicodeEncodeError: 'latin-1' codec can't encode character u'\u201c' in position 0: ordinal not in range(256)

解决方法：

		self.conn.select_db('ark1')
		self.conn.set_character_set('utf8')
		self.cur = self.conn.cursor()
		self.cur.execute("SET NAMES utf8;")
		self.cur.execute("SET CHARACTER SET utf8;")
		self.cur.execute("SET character_set_connection=utf8;")

**运行python 爬虫时，时不时出现下面的错误：**

		httplib.IncompleteRead: IncompleteRead(3623 bytes read)

解决办法：

		try:
		page = urllib2.urlopen(urls).read()
		except httplib.IncompleteRead, e:
		page = e.partial

解决办法2：

	import httplib
	httplib.HTTPConnection._http_vsn = 10
	httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'
	#after | back to http 1.1
	httplib.HTTPConnection._http_vsn = 11
	httplib.HTTPConnection._http_vsn_str = 'HTTP/1.1'
