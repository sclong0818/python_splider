# python

## python elasticsearch

安装

    pip install elasticsearch

## python & mysql

    import MySQLdb

    conn= MySQLdb.connect(
            host='192.168.1.1',
            port = 3306,
            user='root',
            passwd='root'
            #, db ='test',
            )
    conn.select_db('test')
    cur = conn.cursor()
    cur.execute("SET NAMES utf8")

### 常用函数

- commit() 提交
- rollback() 回滚

cursor用来执行命令的方法:
- callproc(self, procname, args):用来执行存储过程,接收的参数为存储过程名和参数列表,返回值为受影响的行数
- execute(self, query, args):执行单条sql语句,接收的参数为sql语句本身和使用的参数列表,返回值为受影响的行数
- executemany(self, query, args):执行单挑sql语句,但是重复执行参数列表里的参数,返回值为受影响的行数
- nextset(self):移动到下一个结果集

cursor用来接收返回值的方法:
- fetchall(self):接收全部的返回结果行.
- fetchmany(self, size=None):接收size条返回结果行.如果size的值大于返回的结果行的数量,则会返回cursor.arraysize条数据.
- fetchone(self):返回一条结果行.
- scroll(self, value, mode='relative'):移动指针到某一行.如果mode='relative',则表示从当前所在行移动value条,如果 mode='absolute',则表示从结果集的第一行移动value条

### 常用技巧

    #最后插入行的主键ID
    print "ID of last record is ", int(cursor.lastrowid)
    #最新插入行的主键ID，conn.insert_id()一定要在conn.commit()之前，否则会返回0
    print "ID of inserted record is ", int(conn.insert_id())

## python & bs4

通过 bs4 select 或者 find 返回soup对象，可以继续调用bs4相关函数

### select

select() 是从BeautifulSoup对象中索取网页元素，并用css选择器寻找元素，不同的选择器模式可以进行组合，禅师复杂配对

    # 搜索id=author 的p标签
    soup.select('p #author')

常用CSS 选择器，更多CSS选择器参看w3cschool的文档：
  - soup.select('div')
  - soup.select('#author')，ID搜索
  - soup.select('.notice')
  - soup.select('div span') ，div内所有span 元素
  - soup.select('div > span') ，div内所有span 元素，必须完全符合路径才能搜索到
  - soup.select('input[name]')，属性存在，搜索存在name 的input 元素
  - soup.select('input[type="button"]')，属性匹配，搜索type=button的input元素
  - soup.select('[class*=clearfix]')，类名搜索，查找class包含了clearfix 的元素
  - soup.select('#link ~ .clearfix'),兄弟搜索，找到id为link标签的所有class=clearfix的兄弟标签
  - soup.select('n nth-of-type(3)'),序列搜索，选择第三个p标签 3 替换成 odd 表示奇数p标签 even ,n,3n 的倍数p标签 ,3n+1 表示 第 4，10 ..个元素


### find 和 find_all

    find_all(name,attrs,recursive,text,**kwargs)
    find(name,attrs,recursive,text,**kwargs)

find 返回的是匹配的第一个结果，find_all 返回的是所有的匹配结果

参数的含义

**name：**name参数可以查找所有名字为name的tag，name值可以有很多：标签、字符串、RE、甚至是函数方法等等

eg 1:标签 tag name

    #查找所有b标签
    soup.find_all('b')

eg 2:正则表达式

    #查找所有以b开头的标签
    soup.find_all(re.compile('^b'))

eg 3: 传一个list 或者 dictionary。

      # 查找所有的<title> 和 <p>标签，后一种方法快一些
      soup.find_all(['title','p'])
      soup.find_all({'title':True,'p':True})
eg 4: 传一个True值，这样可以匹配每个tag的name，也就是匹配每个tag

    soup.find_all(True)

eg 5: 传入 定义的一个函数

    def has_class_but_no_id(tag):
        return tag.has_attr('class') and not tag.has_attr('id')
    #将该函数 传入，将得到所有有class属性无id的标签
    soup.find_all(has_class_but_no_id)

**keywords:** keywords在方法参数中并没有明示，但是能帮我们筛选tag的属性

    soup.find_all('p',align='center')

**attrs:** attrs是一个字典，可以是用attrs去匹配那些名字为Python保留字的属性，例如class,for,name,recursive,limit等等

    soup.find_all(attrs={'id':re.compile("para$")})

**text** text 参数用于搜索文档中的字符串内容。与name参数一样是可选参数，text参数接受字符串，正则表达式，列表，True

    # 搜索文档中含有“one”的字符串
    soup.find_all(text='one')

**recursive:* recuresive是一个boolean 参数，表示是否检索当前tag的所有子孙节点
