from MySQLUtil import MySQLUtil
import time
import random

db = MySQLUtil()


# Divide the frequency of keywords (> 1k) into 4 bins:
# [> 100k], total 64, sample 64
# [10k - 100k), total 927, sample 24
# [5k - 10k), total 793, sample 6
# [1k - 5k), total 4240, sample 6
def pick100keywords():
    l_keywords = []
    # [min_freq, max_freq, sample_number]
    l_bins = [[100000, 10000000, 64],
              [10000, 100000, 24],
              [5000, 10000, 6],
              [1000, 5000, 6]]
    for l_bin in l_bins:
        l_keywords.extend(randomNKeywordsByFrequencyRange(l_bin[0], l_bin[1], l_bin[2]))
    # shuffle the order of keywords
    random.shuffle(l_keywords)
    return l_keywords


def randomNKeywordsByFrequencyRange(p_min_freq, p_max_freq, p_n):
    l_sql = 'SELECT p.word, p.count FROM ' \
            '  (SELECT t.word, t.count FROM limitdb.wordcount t ' \
            '    WHERE t.count >= ' + str(p_min_freq) + \
            '      and t.count < ' + str(p_max_freq) + \
            '  ) p ORDER BY RAND()' \
            'LIMIT ' + str(p_n)
    return db.query(l_sql)


database = 'MySQL'
tableName = 'coordtweets'
keywords = pick100keywords()  # [('job', 3100000)]
ks = [1000, 5000, 10000, 50000, 100000, 500000, 1000000, 2000000, 3000000]
orderBy = 'id'


# For given p_tableName and p_k,
# run the same query limit p_k for all the p_keywords,
# and average the query time as the final execution time of this p_k
def execTimeLimitK(p_tableName, p_keywords, p_k):
    executionTime = 0.0
    queryCount = 0
    for kw in p_keywords:
        if kw[1] < p_k:
            continue
        print 'sending limit ' + str(p_k) + ' query for keyword: ' + kw[0]
        # send limit k query to db
        start = time.time()
        db.queryLimit(p_tableName, kw[0], p_k)
        end = time.time()
        executionTime += (end - start)
        queryCount += 1
    return [p_k, executionTime / queryCount]


print '================================================='
print '  ' + database + '  Experiments - 3.1 Time of limit K'
print '================================================='
print 'table: ', tableName
print 'keywords: ', keywords
print 'K values: ', ks
print '-------------------------------------------------'
execTime1 = []
for k in ks:
    # send dummy queries to warm up the database
    dummy_sql = 'select count(1) from (select t.text from limitdb.dummy_table t where t.id < 865350497200371700) p ' \
                'where p.text like \'%lo%\' '
    startT = time.time()
    db.query(dummy_sql)
    endT = time.time()
    print 'sending dummy query, takes ', str(endT - startT), ' seconds.'
    execTime1.append(execTimeLimitK(tableName, keywords, k))
    # restart the MySQL server
    db.restart()
print '================================================='
print '  ' + database + '  Results - 3.1 Time of limit K'
print '================================================='
print 'table: ', tableName
print 'keywords: ', keywords
print 'K values: ', ks
print '-------------------------------------------------'
for line in execTime1:
    s_arr = [str(a) for a in line]
    print ', '.join(s_arr)


# For given p_tableName and p_k,
# run the same query limit p_k order by p_orderBy for all the p_keywords,
# and average the query time as the final execution time of this p_k
def execTimeLimitKOrderBy(p_tableName, p_keywords, p_k, p_orderBy):
    executionTime = 0.0
    queryCount = 0
    for kw in p_keywords:
        if kw[1] < p_k:
            continue
        print 'sending limit ' + str(p_k) + ' order by ' + p_orderBy + ' query for keyword: ' + kw[0]
        # send limit k order by id query to db
        start = time.time()
        db.queryLimitOrderBy(p_tableName, kw[0], p_k, p_orderBy)
        end = time.time()
        executionTime += (end - start)
        queryCount += 1
    return [p_k, executionTime / queryCount]


print '================================================='
print '  ' + database + '  Experiments - 3.2 Time of limit K & order by ' + orderBy
print '================================================='
print 'table: ', tableName
print 'keywords: ', keywords
print 'K values: ', ks
print '-------------------------------------------------'
execTime2 = []
for k in ks:
    # send dummy queries to warm up the database
    dummy_sql = 'select count(1) from (select t.text from limitdb.dummy_table t where t.id < 865350497200371700) p ' \
                'where p.text like \'%lo%\' '
    startT = time.time()
    db.query(dummy_sql)
    endT = time.time()
    print 'sending dummy query, takes ', str(endT - startT), ' seconds.'
    execTime2.append(execTimeLimitKOrderBy(tableName, keywords, k, orderBy))
    # restart the MySQL server
    db.restart()
print '================================================='
print '  ' + database + '  Experiments - 3.2 Results of limit K & order by ' + orderBy
print '================================================='
print 'table: ', tableName
print 'keywords: ', keywords
print 'K values: ', ks
print '-------------------------------------------------'
for line in execTime2:
    s_arr = [str(a) for a in line]
    print ', '.join(s_arr)

db.close()
