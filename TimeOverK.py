import MySQLUtil as db
import time

database = 'MySQL'
tableName = 'coordtweets'
keywords = ['job', 'water', 'soccer']
orderyBy = 'id'
# Set cache size to be 0 for this session
# deprecated since MySQL 8.0
# db.query("SET SESSION query_cache_size=0;")
# db.commit()


def testTimeOverKForKeyword(p_tableName, p_keyword):
    print 'Table: ' + p_tableName
    print 'Keyword: ' + p_keyword

    executionTime = []
    for k in [1, 10, 100, 1000, 10000, 50000, 100000, 500000, 1000000, 2000000, 3000000]:
        print 'sending limit ' + str(k) + ' query'
        # send limit k query to db
        start = time.time()
        db.queryLimit(p_tableName, p_keyword, k)
        end = time.time()
        executionTime.append([k, (end - start)])
        # send dummy query to clear cache/buffer of DB
        # print '... sending dummy query ...'
        # sql = 'select * from limitdb.dummy_table'
        # db.query(sql)

    print '---------------------------------'
    for et in executionTime:
        print str(et[0]) + ', ' + str(et[1])


print '================================================='
print '  ' + database + '  Experiments - 3.1 Time over K'
print '================================================='

for keyword in keywords:
    testTimeOverKForKeyword(tableName, keyword)
    print '------------------------------------------------'


def testTimeOverKandOrderByForKeyword(p_tableName, p_keyword, p_orderBy):
    print 'Table: ' + p_tableName
    print 'Keyword: ' + p_keyword
    print 'Order by: ' + p_orderBy

    executionTime = []
    for k in [1, 10, 100, 1000, 10000, 50000, 100000, 500000, 1000000, 2000000, 3000000]:
        print 'sending limit ' + str(k) + ' & order by query'
        # send limit k & order by query to db
        start = time.time()
        db.queryLimitOrderBy(p_tableName, p_keyword, k, p_orderBy)
        end = time.time()
        executionTime.append([k, (end - start)])
        # send dummy query to clear cache/buffer of DB
        # print '... sending dummy query ...'
        # sql = 'select * from limitdb.dummy_table'
        # db.query(sql)

    print '---------------------------------'
    for et in executionTime:
        print str(et[0]) + ', ' + str(et[1])


print '================================================='
print '  ' + database + '  Experiments - 3.2 Time over K & order by'
print '================================================='

for keyword in keywords:
    testTimeOverKandOrderByForKeyword(tableName, keyword, orderyBy)
    print '------------------------------------------------'

db.close()
