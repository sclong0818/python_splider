# -*- coding: utf-8 -*-
import MySQLdb

class SMZDM_Mysql:
    def test_print(self):
        print 'hello SMZDM_Mysql'
    def init_db(self):
        print u'数据库连接初始化.....'
        self.conn= MySQLdb.connect(
                host='192.168.0.118',
                port = 3306,
                user='root',
                passwd='root'
                )
        self.conn.select_db('ark1')
        self.conn.set_character_set('utf8')
        self.cur = self.conn.cursor()
        self.cur.execute("SET NAMES utf8;")
        self.cur.execute("SET CHARACTER SET utf8;")
        self.cur.execute("SET character_set_connection=utf8;")
        print u'数据库连接初始化正常.....'

    def close_db(self):
        self.cur.close()
        self.conn.close()
        print u'关闭数据库连接.....'

    def commit(self):
        self.conn.commit()

    def get_conn(self):
        # 曝露 conn
        return self.conn

    def update_mall_categories(self,sqlvalues):
        self.cur.execute('update mall set categories=%s where name=%s',sqlvalues)

    def insert_malls(self,sqlvalues):
        self.cur.executemany('insert into mall(name,categories,uri,excerpt,summary,recommend,pic_url,url,country_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',sqlvalues)

    def insert_category(self,category):
        self.cur.execute('insert into category(name,parent_id,level,uri) values(%s,%s,%s,%s)',[category['name'],category['parent_id'],category['level'],category['uri']])

    def get_big_categories(self):
        self.cur.execute('select id,name,uri from category where level=0 and is_show=1')
        return self.cur.fetchall()

    def get_country(self):
        self.cur.execute('select id,name,zh_name,code,code2 as zipcode from country where is_show=1')
        return self.cur.fetchall()

    def insert_brands(self,sqlvalues):
        self.cur.executemany('insert into brand(name,description,pic_url,country_id,category_id,hot_tag) values(%s,%s,%s,%s,%s,%s)',sqlvalues)

    def get_tags(self):
        self.cur.execute('select id,name,hot_tag from tag')
        return self.cur.fetchall()

    def insert_tags(self,sqlvalues):
        self.cur.executemany('insert into tag(name,hot_tag,hot) values(%s,%s,%s)',sqlvalues)
