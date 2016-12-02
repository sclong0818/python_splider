# -*- coding: utf-8 -*-
import MySQLdb

conn= MySQLdb.connect(
        host='192.168.0.118',
        port = 3306,
        user='root',
        passwd='root'
        #, db ='a10',
        )
conn.select_db('ark1')
cur = conn.cursor()
cur.execute("SET NAMES utf8")
cur.execute('drop TABLE if exists test')
cur.execute('create table test(id int ,info varchar(20))')

#单条插入
value = [1,'hi alex']
cur.execute('insert into test values(%s,%s)',value)

#批量插入
values = []
for i in range(10):
    values.append((i,'我是 hi alex'+str(i)))

print values

cur.executemany('insert into test values(%s,%s)',values)

#更新
cur.execute('update test set info="i am alex" where id=3')

# 查询所有
count = cur.execute("select * from test")

alldata = cur.fetchall()

if alldata:
    for rec in alldata:
        print rec[0], rec[1]


print '-----------'
# fetchmany
count = cur.execute("select * from test")
print 'there is %s rows record' % count
manylist = cur.fetchmany(5)
for b in manylist:
    print b

#一定要有conn.commit()方法来提交事务
conn.commit()
#回滚
#conn.rollback()
cur.close()
conn.close()
